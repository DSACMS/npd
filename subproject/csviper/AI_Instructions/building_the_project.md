

Please read the AI_Instructions/core_design.md to understand the final design of the project. 

We have successfully created the a working prototype of all the steps. Now lets make the following improvements.
Lets complete these tasks one at a time. Focus only on the top item on this list until it is complete. .


* I think expecting a "cacascade" of configuration changes to pass through the system may be unrealistic. 
* Instead I think the "trample" parameter (which is not called that) should be the way this is controlled. 

* Need to refactor things to not include file names with dates in the various files.. need to work on the same nppes files with two different date strings for instance.

* The next thing to fix is the testing infrastructure, every file in the testing subdirectories tests a different problematic data pattern or metadata problem or whatever. 
* These need to be cataloged and turned into automatic tests. 
* However, I think it may be nessecary to rethink how the testing works, in order to think in terms of bad files and corresponding output. 
* I am also concerned that testing part of the project takes place in another repo altogether to avoid cases where the command line tool works differently in the project directory than it does when used as a CLI tool elsewhere.  
