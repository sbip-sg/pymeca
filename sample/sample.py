# %%
"""
This is a sample script to illustrate the MECA DAO workflow.
"""
# %%
# MECA DAO entities setup for illustration purposes. In practice, users will use their own on-chain identity to participate in MECA DAO.
import sys
import os

project_path = os.path.abspath("..")
sys.path.append(project_path)
print(sys.path)
import random

random.seed(0)

from pymeca.utils import generate_meca_simulate_accounts

accounts = generate_meca_simulate_accounts()
print(accounts)

# MECA DAO initiator deploys all contract and publish the addresses
# in this sample we assume doa_owner is the initiator and has deployed the contract and published the below addresses

addresses = {
    "dao_contract_address": "0x7829ad34690d2E8f5559F0499Fed0DE08D3A8137",
    "scheduler_contract_address": "0xba44aefD624ad76343E047DE0A8e518A1602E90b",
    "host_contract_address": "0x0f3F6eFA4dca1d5c9B6dc393f59b7B2ea2aA2F60",
    "tower_contract_address": "0x5346450DBda237C7829F38DcD8322640b73649aA",
    "task_contract_address": "0x1C14F0c76d084D0A917e15837F5cBBFB8a165EaF",
}

import web3
from pymeca.dao import MecaDAOOwner

web3_instance = web3.Web3(web3.Web3.HTTPProvider("http://localhost:9000"))
try:
    web3_instance.eth.get_block("latest")
except Exception as e:
    assert False, e

meca_dao_owner = MecaDAOOwner(
    w3=web3_instance,
    private_key=accounts["meca_dao"]["private_key"],
    contract_address=addresses["dao_contract_address"],
)

# %%
# other MECA DAO entities joins the DAO with their on-chain identity

from pymeca.user import MecaUser
from pymeca.host import MecaHost
from pymeca.tower import MecaTower
from pymeca.task import MecaTaskDeveloper


meca_user = MecaUser(
    w3=web3_instance,
    private_key=accounts["meca_user"]["private_key"],
    dao_contract_address=addresses["dao_contract_address"],
)

meca_host = MecaHost(
    w3=web3_instance,
    private_key=accounts["meca_host"]["private_key"],
    dao_contract_address=addresses["dao_contract_address"],
)

meca_tower = MecaTower(
    w3=web3_instance,
    private_key=accounts["meca_tower"]["private_key"],
    dao_contract_address=addresses["dao_contract_address"],
)

meca_task_developer = MecaTaskDeveloper(
    w3=web3_instance,
    private_key=accounts["meca_task"]["private_key"],
    dao_contract_address=addresses["dao_contract_address"],
)

meca_host.register(
    block_timeout_limit=30,
    public_key="0x" + "2" * 128,
    initial_deposit=300,
)

meca_tower.register_tower(
    size_limit=10000,
    public_connection="http://localhost:8080",
    fee=10,
    fee_type=0,
    initial_deposit=300,
)

# %%
# Task developer upload a task
meca_task_developer.register_task(
    ipfs_sha256="0x" + "1" * 64,
    fee=10,
    computing_type=0,
    size=1024,
)

# %%
# host register its connection with tower
print(meca_host.get_my_towers())
meca_host.register_for_tower(tower_address=meca_tower.account.address)

# %%
# tower register a host to itself
print(meca_tower.get_pending_hosts())
meca_tower.accept_host(host_address=meca_host.account.address)
print(meca_tower.get_my_hosts())

# %%
# host register a task
print(meca_host.get_my_towers())
print(meca_host.get_my_tasks())
meca_host.add_task(ipfs_sha256="0x" + "1" * 64, block_timeout=7, fee=10)
print(meca_host.get_my_tasks())

# %%
# meca user check the blockchain to determine the tower and host
towers_hosts = meca_user.get_towers_hosts_for_task(
    ipfs_sha256="0x" + "1" * 64,
)


# meca user app implements its own logic to select the tower and host
def select_tower_and_host(towers_hosts):
    return towers_hosts[0]["towerAddress"], towers_hosts[0]["hostAddress"]


selected_tower, selected_host = select_tower_and_host(towers_hosts)
print(selected_tower, selected_host)

# %%
# meca user propose a task request with the selected tower and host.
success, task_id = meca_user.send_task_on_blockchain(
    ipfs_sha256="0x" + "1" * 64,
    host_address=selected_host,
    tower_address=selected_tower,
    input_hash="0x" + "8" * 64,
)
# the input is encrypted with the hosts public key and send to the tower

# %%
# execution of the task
# 1. tower receives the task request from user and stores the input locally (not shown here)
# 2. tower check the task to ensure it is valid (Validity can include tower address, host address etc.)
print(meca_tower.get_running_task(task_id=task_id))
# 3. tower send the task to the host (not shown here)
# 4. host retrieve the input from tower and check the task is valid (not shown here)
print(meca_host.get_running_task(task_id=task_id))
# 5. host execute the task (not shown here)
# 6. host store the output locally (not shown here)


# %%
# meca user pull the results from the tower
# meca user acknowledge the task request completion
meca_user.finish_task(task_id=task_id)

# %%
# participants can leave the MECA DAO

# %%
# host delete its active task, empty its queue and leave MECA DAO
meca_host.delete_task(ipfs_sha256="0x" + "1" * 64)
print(meca_host.get_my_tasks())
meca_host.update_block_timeout_limit(new_block_timeout_limit=0)
meca_host.unregister()

# %%
# tower delete empty its queue and leave MECA DAO
meca_tower.update_tower_size_limit(new_size_limit=0)
meca_tower.delete_tower()
