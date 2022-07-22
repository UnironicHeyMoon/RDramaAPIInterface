# RDramaAPIInterface
*Sneed, BIPOC-twink*

## What

This is an API interface for writing various things for rdrama, notorious gay porn sharing site.

## Setup

### Get the code

So, getting the code all set up can be a bit of a pain because this is a script that is meant to be called by other scripts. If I was a NERD I would try to create a pip package that you could install, but I have tried that before and it was a NIGHTMARE. I am NOT doing that again. Someone else can try, I ain't touching that shit with a fifty foot pole. Besides, who really cares, it's not that big of a deal.

You can...
 - clone the repo and then copy the file to whatever project you are working on (okay solution)
 - add it to your python path (probably best)
 
### Get an API token

This is easy, and if you can't figure it out you are kinda dumb tbh

PROTIP: In the part where it asks for a website, you can put anything. (That's just the redirect if you are messing with OAuth). I usually put gaysex.net, but you do you.

Once you request it, beg the world's largest rodent to approve it. If he is merciful, he may allow it.

### Start programming

First, create an instance of the interface. For accessing rdrama.net, here's what you do...

```python
from RDramaAPIInterface import RDramaAPIInterface

rdrama = RDramaAPIInterface(AUTH_TOKEN, "rdrama.net")
```

and then you can do whatever you want!! For example, send me hate mail like this

```python
rdrama.send_message("HeyMoon", "I have had it up to here with your shitty api interface. Fuck you, fuck python, and fuck aevann for making this website.")
```

and your bot will send me a rude message! everythign else should be pretty self-explanatory.

## FAQ

### Q. Can I use this on other sites? 

Yep. Just replace "rdrama.net" with whatever site it is.

### Q. Why can't I connect to my local test instance of rdrama?

probably because you are using https. try this:

'''python

rdrama = RDramaAPIInterface(TEST_AUTH_TOKEN, "rdrama.net", https=False)

'''

### Q. WTF dude, my code was working yesterday and it suddenly started breaking, I literally cannot cope with this

aevann probably fucked around with the code again lmao. ask him what's going on. also, for real, don't be a douche like "ah ha idiot I found an issue in the code". you are an api, aevann is going to prioritize actual users of the site over bots.

### Q. Uhm, HeyMoon, your code is broken

Okay, bucko, see that tab above this document that says *Pull Request*? Be my guest. Like, literally, please make pull requests if there is something that is wrong. I made this specifically for my bots, so I of course left stuff out. 

If you do make a pull request, ping me on discord or on rdrama and I'll take a look king

## License

This code is licensed under the GIGACHAD license. Basically, you can do whatever you want with this code, as long as you charge money for it. I do not want hippies using my software.
