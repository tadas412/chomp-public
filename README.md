# CHOMP

http://devpost.com/software/chomp

Elevator Pitch: UI-less digitization of food truck payments and ordes through Venmo and SMS
It’s built with: python, flask, amazon-web-services, rds, elastic beanstalk, venmo api, javascript, html5, twilio, mysql
Here’s the whole story:
## Inspiration

With every passing day, you see hundreds of new apps being released. Each one of them is vying for a spot on that valuable real estate called your homescreen. And yet, almost all the time you spend on your phone is dedicated to just a handful of apps: the iMessages, Google Maps, and Spotifies of the world. 

Along with this “app boom” there has begun to emerge a new trend. Messaging is poised to be the platform of the future. The rise of NLP and the ability to consolidate mass amounts of information in single services is enabling new seamless, reliable services. “No UI Is The New UI,” as some tech experts are preaching (http://techcrunch.com/2015/11/11/no-ui-is-the-new-ui, http://techcrunch.com/2015/08/16/the-burgeoning-invisible-app-market/). 

We wanted to take this emerging trend and apply it to a topic relevant to our personal daily lives, while doing a little good in the community. Food trucks are a staple of Penn’s campus and Philadelphia’s food culture. Yet they’re notorious for their insistence on cash payments, long lines, and, if available at all, credit card surcharges.

We love going to food trucks, we’ve always wanted a streamlined and convenient payment process, and a way to easily order ahead to pick up. And so Chomp was born.

## What it does

Chomp centralizes the ability to order from any food truck in the system through one phone number. Customers send an SMS to the number to view an abbreviated menu, remind themselves of the location of a food truck, or order from a food truck. Once the vendor accepts, the Venmo charge is sent. Payment is completed through Venmo, and both parties are notified throughout the process. Then the vendor makes the meal and the customer goes to pick it up! 

## How we built it

We utilized Twilio to send/receive SMS messages to/from customers and vendors, the Venmo API to facilitate payments, an AWS RDS MySQL database to store our data, AWS Elastic Beanstalk to host our server, and Python Flask as the framework for both our server management and web UI. 

## Challenges we ran into

We hoped to incorporate an NLP component that made the ordering process less rigid and grammar-free, but ended up focusing our time on ensuring core functionality. Considering the array of services our technology stack utilized, we found integration challenging. Some of the services we were using, in combination with others, had little documentation or online discussion to be utilized, so we ended up doing quite a bit of debugging on our own.

## Accomplishments that we're proud of

First and foremost: having a functional, standalone product that works as expected. It could be deployed as a beta product almost immediately; it’s wonderful to see us go from idea inception to tangible result in about 24 hours. 

We’re particularly glad the integration worked out. Despite several challenging, pesky bugs and hurdles, we worked together to debug each others’ code, didn’t burn out, and constantly kept moving forward.

Perhaps an underrated achievement: this kind of project has so many potential routes and really interesting applications or enhancements we could have pursued, and we were able to effectively distinguish from the needs and the wants. We made sacrifices along the way that allowed us to avoid wasting time and getting caught up in details that weren’t necessary.

## What we learned

Debugging is exponentially faster when you have a partner with a fresh mind take a look at it. Cutting big (excessive) features is a tough but necessary and rewarding part of the development process. There’s a nice balance to hold between using technologies you’re already comfortable with to expedite the development process and technologies you haven’t used before to make sure you’re still learning. 

## What's next for Chomp

Chomp could be quickly morphed into a viable startup. The core functionality as is would already provide value to food carts by expanding their reach with little effort on their end - Chomp could partner with food trucks and start to expand its inventory offering. The product could be monetized by either requiring food trucks to pay some sort of fee for using the service, or passing the costs on to the customer.

Further, Chomp can expand on the technical side through introducing a more robust ordering system. Simplicity is key, and eliminating grammar structure by implementing more sophisticated NLP would.

Chomp’s influence doesn’t need to stop at food trucks. The model is very applicable to restaurants and take-out as well - and it manages to differentiate itself from services like GrubHub or Seamless through its messaging-focused core. No more clunky apps: it’s as easy as texting your mom what’s for dinner tonight. 
