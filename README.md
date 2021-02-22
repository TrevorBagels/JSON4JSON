# JSON4JSON
Advanced and easy to use JSON configuration for python. Lets the developer configure their JSON using JSON. That sounds weird, but it's pretty neat and useful for programs that let users customize the settings via JSON. 

## Rundown

  When using this, you have two files. The first file is the `rules.json` file, which is written by the developer to make life easier. Then, you've got `config.json`, which is written by the user of the developers program. 
  
  Generally, we want our programs to be capable of customization, so that the user can make the program suit their needs. JSON provides a fairly easy way of doing this; the user can edit their preferences in a JSON file without needing to make changes to the source code. 
  
  JSON4JSON is JSON, but it makes the life of the developer (and the user), much easier. Sometimes users enter the wrong information into a config file, causing the program to throw errors if it doesn't already check for missing or incorrectly formatted options. Sometimes developers don't want to tell users exactly how to format certain datatypes, it'd be much easier if something did that automatically. People often argue over the imperial system and the metric system, and users don't like having to convert miles to kilometers. JSON4JSON does all of this automatically, allowing the developer to configure (via `rules.json`) how a config file should be interpreted.
