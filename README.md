# JSON4JSON
Advanced and easy to use JSON configuration for python. Lets the developer configure their JSON using JSON. That sounds weird, but it's pretty neat and useful for programs that let users customize the settings via JSON. 
 
**Can be installed via `pip3 install JSON4JSON`**

## Rundown

  JSON4JSON uses a rules file, written by the developer, to transform a configuration file, written by the user, into something easily usable by the developer. 

## Features
  * Unit conversion
  * Variables (in json!)
  * Rules can apply to specific indexes/ranges of arrays
  * Auto generates missing data, can throw errors if you want it to
  * NOT abandoned
## Why does this exist?

  Generally, we want our programs to be capable of customization, so that the user can make the program suit their needs. JSON provides a fairly easy way of doing this; the user can edit their preferences in a JSON file without needing to make changes to the source code. 
  
  JSON4JSON is JSON, but it makes the life of the developer (and the user), much easier. 
  Sometimes users enter the wrong information into a config file, causing the program to throw errors if it doesn't already check for missing or incorrectly formatted options. All this does is confuse the user, and then they go report it as a bug, when really, they forgot to add something to the config.
  Sometimes developers don't want to tell users exactly how to format certain datatypes, it'd be much easier if something did that automatically. People often argue over the imperial system and the metric system, and users don't like having to convert miles to kilometers. JSON4JSON does all of this automatically, allowing the developer to configure (via `rules.json`) how a config file should be interpreted.
