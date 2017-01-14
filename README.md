# INFO-256-RoboJoker
Final project for INFO 256

***
**To Run the App**:  
`pip install requirements.txt` (only need to do this once)  
`python run.py`  

**Heroku Commands**:  
`git push heroku master`  
additional info: [deploying code into Heroku](https://devcenter.heroku.com/articles/git#deploying-code)

**Reference: Git Commands**:  
Change branch locally -  
`git checkout local_branch_name`  

Normal commit -  
`git add .`  
`git commit -m 'your message here'`  
`git push origin branch_name`  

Discard an unsaved change on your local branch -  
`git clean -df`  
`git checkout -- .`  

Force push to remote branch -   
`git push -f origin branch_name`  

Force sync from remote branch (override all your local changes) -   
`git fetch`  
`git reset --hard origin/branch_name`  
