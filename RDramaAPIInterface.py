import time
import requests
from bs4 import BeautifulSoup
import traceback
import backoff

class TimeOutException(Exception):
    pass

'''
Wrapper around the RDRama API
'''
class RDramaAPIInterface:
    def __init__(self, authorization_token, site, https: bool = True) -> None:
        self.headers={"Authorization": authorization_token}
        self.site = site
        self.protocol = "https" if https else "http"

    def make_post(self, title, submission_url, body):
        url=f"{self.protocol}://{self.site}/submit"
        return self.post(url, data={'title' : title, 'url': submission_url, 'body': body})

    '''
    Sends a message to a user.
    '''
    def send_message(self, username, message):
        url=f"{self.protocol}://{self.site}/@{username}/message"
        return self.post(url, data={'message':message})

    '''
    Replies to the comment with the given id.
    '''
    def reply_to_comment(self,parent_fullname, parent_submission, message, file=None):
        url=f"{self.protocol}://{self.site}/comment"
        if file == None:
            return self.post(url, data={
                'parent_fullname':parent_fullname,
                'submission': parent_submission,
                "body": message
                })
        else:
            return self.post(url, data={
                'parent_fullname':parent_fullname,
                'submission': parent_submission,
                "body": message
                }, files=file)

    '''
    Replies to the comment with the given id.
    '''
    def reply_to_comment_easy(self,comment_id, parent_submission, message, file=None):
        return self.reply_to_comment(f"c_{comment_id}", parent_submission, message, file=file)

    def reply_to_post(self, post_id, message):
        return self.reply_to_comment(f"p_{post_id}", post_id, message)

    '''
    Gets "all" comments.
    '''
    def get_comments(self, number_of_pages=1, user=None, sort="new", upper_bound = 0, lower_bound = 0):
        if (user == None):
            url=f"{self.protocol}://{self.site}/comments"
        else:
            url=f"{self.protocol}://{self.site}/@{user}/comments"
        
        params = f"?sort={sort}&t=all&before={upper_bound}&after={lower_bound}"
        url+=params
        
        if number_of_pages == 1:
            return self.get(url)
        else:
            results = []
            for i_ in range(number_of_pages):
                i = i_ + 1
                full_url=f"{url}?page={i}"
                results += self.get(full_url)['data']
            return {
                'data': results
            }
            

    '''
    Calls the notifications endpoint
    '''
    def get_notifications(self, page : int):
        url=f"{self.protocol}://{self.site}/notifications?page={page}"
        return self.get(url)

    def reply_to_direct_message(self, message_id : int, message : str):
        url=f"{self.protocol}://{self.site}/reply"
        return self.post(url, data = {
            'parent_id' : message_id,
            'body': message
        }, allowed_failures=[500])

    def get_comment(self, id):
        url=f"{self.protocol}://{self.site}/comment/{id}"
        return self.get(url)

    def get_front_page(self):
        url=f"{self.protocol}://{self.site}"
        return self.get(url)

    def has_url_been_posted(self, the_url):
        url=f"{self.protocol}://{self.site}/is_repost"
        return self.post(url, {'url': the_url})['permalink'] != ''

    def get_user_information(self, id):
        url=f"{self.protocol}://{self.site}/{id}/info"
        return self.get(url)
    '''
    I have no clue what this is supposed to do, lol.
    '''
    def clear_notifications(self):
        url=f"{self.protocol}://{self.site}/clear"
        return self.post(url, headers=self.headers)

    def get_unread_notifications(self):
        url=f"{self.protocol}://{self.site}/unread"
        return self.get(url)

    def give_coins(self, user, amount):
        url=f"{self.protocol}://{self.site}/@{user}/transfer_coins"
        return self.post(url, data={'amount':amount})

    def get_post(self, id):
        url=f"{self.protocol}://{self.site}/post/{id}"
        return self.get(url)

    '''
    Given a notification, returns whether or not the message is from Drama (ie, the messenger)
    '''
    def is_message_from_drama(self,notification) -> bool:
        return notification['author_name'] == "Drama" or notification['author']['id'] == 1

    '''
    IMPLYING THAT THE MESSAGE IS FROM DRAMA, determines whether or not the notification is a gift transaction.
    '''
    def is_message_is_a_gift_transaction(self,notification) -> bool:
        soup = BeautifulSoup(notification['body_html'], 'html.parser')
        p = soup.p
        #The first element is :marseycapitalistmanlet:. If not, we know this isn't a gift
        marsey_capitalist_manlet = p.contents[0]

        return (marsey_capitalist_manlet.name == "img" and marsey_capitalist_manlet['alt'] == ":marseycapitalistmanlet:")        


    '''
    Whether or not the message is a follow notification.
    '''
    def is_message_a_follow_notification(self, notification):
        return "has followed you!" in notification['body_html']
    
    '''
    Whether or not the message is an unfollow notification.
    '''
    def is_message_an_unfollow_notification(self, notification):
        return "has unfollowed you!" in notification['body_html']

    '''
    Parses a gift transaction
    '''
    def parse_gift_transaction(self, notification):
        soup = BeautifulSoup(notification['body_html'], 'html.parser')
        p = soup.p
        #The third element is the username. It is a hyperlink tag containing the name of the user
        user_element = p.contents[2]
        user_id = user_element['href'].split("/")[2] #the hyperlink is formatted like so: /id/x, where x is the id
        user_name = user_element.contents[1].string[1:] #the username is within the image tag. we remove the first character, which is an @

        #the fourth element is the "gift" string. It looks like this " has gifted you x coins".
        amount_string = p.contents[3]
        amount = amount_string.string.split(" ")[4]

        return {
            "type": "transfer",
            "user_name": user_name,
            "user_id": int(user_id),
            "amount": int(amount),
            "id": notification['id']
        }

    '''
    parses a post mention
    '''
    def parse_post_mention(self, notification):
        soup = BeautifulSoup(notification['body_html'], 'html.parser')
        p = soup.p
            
        #The first element is the username. It is a hyperlink tag containing the name of the user
        user_element = p.contents[0]
        user_id = user_element['href'].split("/")[2] #the hyperlink is formatted like so: /id/x, where x is the id
        user_name = user_element.contents[1].string[1:] #the username is after the img tag. we remove the first character, which is an @

        post_element = p.contents[-1]
        post_id = post_element['href'].split("/")[2]
        post_name = post_element.string

        return {
            "type": "post_mention",
            "user_name": user_name,
            "user_id": int(user_id),
            "id": notification['id'],
            "post_name": post_name,
            "post_id": post_id
        }

    '''
    parses a follow notification
    '''
    def parse_follow_notification(self, notification):
        soup = BeautifulSoup(notification['body_html'], 'html.parser')
                
        p = soup.p

        #The first element is the username. It is a hyperlink tag containing the name of the user
        user_element = p.contents[0]
        user_id = user_element['href'].split("/")[2] #the hyperlink is formatted like so: /id/x, where x is the id
        user_name = user_element.contents[1].string[1:] #the username is after the img tag. we remove the first character, which is an @


        return {
            "type": "follow",
            "user_name": user_name,
            "user_id": int(user_id),
            "id": notification['id']
        }

    '''
    parses an unfollow notification
    '''
    def parse_unfollow_notification(self, notification):
        soup = BeautifulSoup(notification['body_html'], 'html.parser')
                
        p = soup.p

        #The first element is the username. It is a hyperlink tag containing the name of the user
        user_element = p.contents[0]
        user_id = user_element['href'].split("/")[2] #the hyperlink is formatted like so: /id/x, where x is the id
        user_name = user_element.contents[1].string[1:] #the username is after the img tag. we remove the first character, which is an @

        return {
            "type": "unfollow",
            "user_name": user_name,
            "user_id": int(user_id),
            "id": notification['id']
        }

    '''
    parses a dm
    '''
    def parse_direct_message(self, notification):
        soup = BeautifulSoup(notification['body_html'], "html.parser")
        message = ''.join(soup.findAll(text=True))
        return {
            "type": "direct_message",
            "user_name": notification['author_name'],
            "user_id": notification['author']['id'],
            "id": notification['id'],
            "message_html": notification['body_html'],
            "message": message
        }

    '''
    parses a reply to a comment.
    '''
    def parse_comment_reply(self, notification):
        #TODO: Lots of changes needed.
        return {
            "type": "comment_reply",
            "parent_id": notification["id"],
            "post_name": notification["post"]["title"],
            "post_id": notification["post"]["id"]
        }

    def parse_comment_mention(self, notification):
        #TODO: Work needs to be done here, I removed some stuff
        return {
            "type": "comment_mention",
            "user_name": notification['author_name'],
            "user_id": notification['author']['id'],
            "id": notification["id"],
            "message": notification['body'],
            "parent_comment_id": notification['parent_comment_id'] if notification['level'] != 1 else None,
            "post_id": notification['post_id']
        }

    '''
    Returns a list of notifications in an easy to process list.
    '''
    def get_parsed_notification(self):
        to_return = []
        notifications = self.get_unread_notifications()['data']
        if (notifications == []):
            return []
        for notification in notifications:
            parsed_notification = {}
            try:
                if self.is_message_from_drama(notification):
                    if (self.is_message_is_a_gift_transaction(notification)):
                        parsed_notification = self.parse_gift_transaction(notification)
                    elif ("has mentioned you: " in notification['body_html']):
                        parsed_notification = self.parse_post_mention(notification)
                    elif (self.is_message_a_follow_notification(notification)):
                        parsed_notification = self.parse_follow_notification(notification)
                    elif (self.is_message_an_unfollow_notification(notification)):
                        parsed_notification = self.parse_unfollow_notification(notification)
                    elif (self.welcome_message in notification['body_html']):
                        #Welcome message
                        pass
                    elif ("if you don't know what to do next" in notification['body_html']):
                        #API approval message
                        pass
                    else:
                        pass
                elif notification['post_id'] == 0:
                    #Direct message
                    parsed_notification = self.parse_direct_message(notification)
                elif notification['author_name'] == "HMSE":
                    #comment reply
                    parsed_notification = self.parse_comment_reply(notification)
                else:
                    #comment mention
                    parsed_notification = self.parse_comment_mention(notification)
                to_return.append(parsed_notification)
            except BaseException as e:
                print(f"Exception {e}")
                print(f"Notification: {notification}")
                traceback.print_exc()
            
        return to_return

    @backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException)
    def get(self, url, allowed_failures = []):
        response = requests.get(url, headers=self.headers)
        print(f"GET {url} ({response.status_code})")
        if (response.status_code == 429):
            raise requests.exceptions.RequestException()
        if (response.status_code != 200 and response.status_code not in allowed_failures):
            raise BaseException(f"GET {url} ({response.status_code}) {response.json()}")
        else:
            return response.json()
    
    @backoff.on_exception(backoff.expo,
                      TimeOutException)
    def post(self, url, data, allowed_failures = [], files = None):
        if files == None:
            response = requests.post(url, headers=self.headers, data=data)
        else:
            response = requests.post(url, headers=self.headers, data=data, files=files)
        print(f"POST {url} ({response.status_code}) {data}")
        if (response.status_code == 429):
            raise TimeOutException
        if (response.status_code != 200  and response.status_code not in allowed_failures):
            raise BaseException(f"POST {url} ({response.status_code}) {data} => {response.json()}")
        else:
            return response.json()
