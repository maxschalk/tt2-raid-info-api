IF [%1]==[] (
    SET "CommitMessage=automated: :rocket: force deploy from dev"
) ELSE (
    SET "CommitMessage=%1"
)

git checkout dev

git add .

git commit -am %CommitMessage%

git checkout main

git merge dev

git push --all

git checkout dev

