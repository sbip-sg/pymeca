# pymeca

A python package for interacting with the MECA smart contracts

## Installation

```bash
pip install pymeca
```

## Build from source

```bash
git clone https://github.com/sbip-sg/pymeca.git
cd pymeca
git submodule init
git submodule update --recursive
pip install poetry
poetry install
```

## Run tests

Requirements: poetry
```bash
pip install poetry
poetry install
cd ./meca-contracts/src/ganach && npm install
```

Requirements: node.js 20.11.1 and npm (tested with 8.5.5)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="${HOME}/.nvm" && ."$NVM_DIR/nvm.sh"
cd meca-contracts/src/ganache && nvm install .nvmrc && nvm use .nvmrc && nvm install-latest-npm && npm install
```

From the main directory:
```bash
poetry shell
pytest
```


## Usage


Launch the ganache test chain in a terminal to watch

```bash
cd src/pymeca/scripts
python3 ganache.py \
--host http://localhost \
--port 9000 \
--ganache-server-script-path ../../../meca-contracts/src/ganache/index.js \
--generate-accounts \
--accounts_file_path ../../config/accounts.json \
--dao-address-file-path ../dao_contract_address.txt \
--dao-file-path \
../../../meca-contracts/src/contracts/MecaContract.sol \
--scheduler-file-path \
../../../meca-contracts/src/contracts/SchedulerContract.sol \
--host-file-path \
../../../meca-contracts/src/contracts/HostContract.sol \
--tower-file-path \
../../../meca-contracts/src/contracts/TowerContract.sol \
--task-file-path \
../../../meca-contracts/src/contracts/TaskContract.sol \
--scheduler-fee 100 \
--host-register-fee 100 \
--host-initial-stake 100 \
--host-task-register-fee 100 \
--host-failed-task-penalty 100 \
--tower-initial-stake 100 \
--tower-host-request-fee 100 \
--tower-failed-task-penalty 100 \
--task-addition-fee 100
```

- A sample workflow of how DAO entities interact with each other is provided [here](./sample/sample.py). The sample assumes that a ganache chain launched with the sample commands with [ganache.py](./src/pymeca/scripts/ganache.py) to setup corresponding accounts.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`pymeca` was created by Stefan-Dan Ciocirlan (sdcioc). It is licensed under the terms of the MIT license.

## Credits

`pymeca` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).

