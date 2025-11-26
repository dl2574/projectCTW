# ProjectCTW Summary
## Summary
This project directory contains a django project for a volunteer application called projectCTW, which stands for Project Change The World.

The purpose of this application is to enable users to propose "events" to other users. These events are volunteer project ideas which the proposing user thinks would be a helpful event within their community. Some examples of event proposals could be to create a community garden in a low income area of town, clean up a run down park, pickup debris after a storm, etc.

Once a proposal is made, users can view a list of all proposals and upvote ones they think are good ideas and would want to participate in. If an event receives enough upvotes, it is moved from a proposal status to a planning status and the users who upvoted the event are notified. In the planning stage, users vote on a date to hold the event, create a supply list of required supplies, and work additional event details. Sponsors, an additional type of account which can be created by businesses, can then choose to sponsor specific events by supplying items on the item list or additional support.

Once an approved event date has been reached, the event moves into an execution status. While in this status, users can "check-in" to the event and receive a verified attendance for the event. After the event is complete, a summary of what was accomplished is created and the event is added to attendee's event resume's which is maintained by the site. 

## Required packages
Read the requirements.txt file in the project's root directory for additional packages being used.

## CI/CD
This project has a CI/CD pipeline established with railway.
- All development is being completed on the development branch
- Once test pass, changes are merged into the main branch
- Any updates to the main branch run a github action to run all tests.
- If all tests pass, railway rebuilds the site and deploys it to www.projectctw.com
