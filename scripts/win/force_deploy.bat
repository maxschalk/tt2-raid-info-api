git checkout dev

git add .

git commit -am "automatic: force deploy from dev"

git checkout main

git merge dev

git push --all

git checkout dev