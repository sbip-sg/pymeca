# CHANGELOG

## v0.1.2 (2024-09-06)

### Fix

* fix: update pyproject.toml ([`b7df8af`](https://github.com/sbip-sg/pymeca/commit/b7df8af2615a9fe9ec4726b44384e5e030dfb8f3))

## v0.1.1 (2024-09-06)

### Fix

* fix: update README.md ([`9256b4d`](https://github.com/sbip-sg/pymeca/commit/9256b4d9ffdf19c81aa8ca5e4d76042041efb7f1))

* fix: rename (#10)

* rename project

* change relative path and the submodule ref

* Update submodule

---------

Co-authored-by: hugy718 &lt;hugy718@gmail.com&gt; ([`8f3c0f4`](https://github.com/sbip-sg/pymeca/commit/8f3c0f448c799b7b88845399e8b98c4f1a7cb079))

## v0.1.0 (2024-07-24)

### Feature

* feat: release ([`1b31821`](https://github.com/sbip-sg/pymeca/commit/1b318213eab6490a3851a079ab8949ef7af09910))

### Unknown

* Use tasksent and taskfinished events on contract (#8)

* Updated submodule url to be relative

* created get_all_executed_tasks function

* git submodule commit update

* Updated git submodule reference

* Apply suggestions from code review

Co-authored-by: Lim Junxue &lt;60027105+LimJunxue@users.noreply.github.com&gt;

* Updated git submodule reference

* Updated git submodule reference

* Updated git submodule reference

* fixed get_all_executed_tasks function

* Fix return type errors from events

* Updated git submodule reference

* Parse and return Task Event results

* Update meca-contracts ref

* Update .gitmodules

* created get_sent_tasks function

* Fix refactor

* Fix refactor

* Update host.py

---------

Co-authored-by: Lim Junxue &lt;60027105+LimJunxue@users.noreply.github.com&gt;
Co-authored-by: LimJunxue &lt;junxue1@hotmail.com&gt; ([`d0de746`](https://github.com/sbip-sg/pymeca/commit/d0de74632e6aa147d82bebf33e1dd1d05c919886))

## v0.0.2 (2024-07-15)

### Fix

* fix: add the initial input hash for tee tasks inside pymeca (#9)

* add the initial input hash for tee tasks inside pymeca

* bump the meca-contract version

---------

Co-authored-by: hugy718 &lt;hugy718@gmail.com&gt; ([`7db8eba`](https://github.com/sbip-sg/pymeca/commit/7db8eba6515baa82400e2f9ce1f2bddd7c11aa6d))

## v0.0.1 (2024-06-12)

### Fix

* fix: readme ([`6bcdcfa`](https://github.com/sbip-sg/pymeca/commit/6bcdcfa54fe66e1c1c35e77c398c284a6e836521))

### Unknown

* add tee task workflow ([`6c19d73`](https://github.com/sbip-sg/pymeca/commit/6c19d73ed07d7af9fa42bf0dcad604d30e08884a))

* Arguments for deploying to different chains (#6)

* Let user choose blockchain endpoint and more args

* Remove check for port arg ([`842d111`](https://github.com/sbip-sg/pymeca/commit/842d1115ad0c8efd3d365e8cda4bb1f4f6d88a35))

* update the poetry.lock ([`8bd40bb`](https://github.com/sbip-sg/pymeca/commit/8bd40bbc92ac8362d56bbb0bcbd307812d84c456))

* Penalty workflow (#5)

* register hash of output

* add some other functionality for mock users

* improve with fast api

* mock  user

* cleaning the repo and remove mock user to be transfer in another repo ([`1c32d3d`](https://github.com/sbip-sg/pymeca/commit/1c32d3de02db3fdd2b1d6149c4888cecdba2f3df))

* Allow multiple tower connections for hosts, Move resource declaration to host (#4)

* Allow multiple tower connections for hosts

* Move resource declaration to host ([`8fe8465`](https://github.com/sbip-sg/pymeca/commit/8fe846566e0f4520614de4a05246f3b8862935fd))

## v0.0.0 (2024-03-14)

### Unknown

* change the coverage report ([`248f712`](https://github.com/sbip-sg/pymeca/commit/248f712300250b58ebd5872a3aab51fe29cb165c))

* integrate submodules ([`66456a3`](https://github.com/sbip-sg/pymeca/commit/66456a3506345c9638349dbc1fd1cbae17fdeddf))

* Add CI/CD and Docs Github Actions (#3)

* add docs and ci/cd Github Actions ([`4ccd440`](https://github.com/sbip-sg/pymeca/commit/4ccd4404df3d628cb6104e52eacb20c240d36746))

* Mock Actors (#2)

* Add sample script to demo the workflow; improve documentations; fix exception handling of tests when cannot connect to ganache

* Add is_tower_registered to pymeca

* Add cli for actors

* Add function for task dev to add folder to ipfs, add comments

* Add ipfs package

Shift poetry packages into requirements.txt.
Replace encryption of task input with hashing.
Host verifies task hash instead of tower.

* Install ipfs in container

* Re add msg encryption and shift code into functions

---------

Co-authored-by: Lim Junxue &lt;junxue1@hotmail.com&gt;
Co-authored-by: sdcioc &lt;stefan_dan@xn--ciocrlan-o2a.ro&gt; ([`c1a5f31`](https://github.com/sbip-sg/pymeca/commit/c1a5f316fd35ff542f5d699e04a5685719681fd8))

* Docs (#1)

* comments and documentation

* update abi ([`88b6260`](https://github.com/sbip-sg/pymeca/commit/88b62602b2ee7cca0692cfd925e38932e483f541))

* add the interaction with the submodule and eliminate the virtual envs from the docker ([`20791d7`](https://github.com/sbip-sg/pymeca/commit/20791d788c9f75ad0152ebe7393223c6cc735e93))

* initial commit ([`8852f9d`](https://github.com/sbip-sg/pymeca/commit/8852f9d4e805001f82a03452717806ccd5fab38e))
