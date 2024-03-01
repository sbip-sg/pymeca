import pytest
import pymeca.pymeca


# a simple active actor
@pytest.fixture(scope="class")
def active_actor(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.pymeca.MecaActiveActor(
        w3=w3,
        private_key=accounts["meca_user"]["private_key"],
        dao_contract_address=addresses["dao_contract_address"]
    )


class TestActiveActorGetters:
    # dao tests
    def test_get_scheduler_contract_address(
        self,
        active_actor,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        scheduler_contract_address = addresses["scheduler_contract_address"]
        address = active_actor.get_scheduler_contract_address()
        assert address == scheduler_contract_address

    # scheduler tests
    def test_scheduler_flag(
        self,
        active_actor
    ):
        flag = active_actor.get_scheduler_flag()
        assert flag is True

    def test_get_tower_contract_address(
        self,
        active_actor,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        tower_contract_address = addresses["tower_contract_address"]
        address = active_actor.get_tower_contract_address()
        assert address == tower_contract_address

    def test_get_host_contract_address(
        self,
        active_actor,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        host_contract_address = addresses["host_contract_address"]
        address = active_actor.get_host_contract_address()
        assert address == host_contract_address

    def test_get_task_contract_address(
        self,
        active_actor,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        task_contract_address = addresses["task_contract_address"]
        address = active_actor.get_task_contract_address()
        assert address == task_contract_address

    def test_get_scheduler_fee(
        self,
        active_actor,
        SCHEDULER_FEE
    ):
        fee = active_actor.get_scheduler_fee()
        assert fee == SCHEDULER_FEE

    # host tests
    def test_get_host_register_fee(
        self,
        active_actor,
        HOST_REGISTER_FEE
    ):
        fee = active_actor.get_host_register_fee()
        assert fee == HOST_REGISTER_FEE

    def test_get_host_task_register_fee(
        self,
        active_actor,
        HOST_TASK_REGISTER_FEE
    ):
        fee = active_actor.get_host_task_register_fee()
        assert fee == HOST_TASK_REGISTER_FEE

    def test_get_host_initial_stake(
        self,
        active_actor,
        HOST_INITIAL_STAKE
    ):
        stake = active_actor.get_host_initial_stake()
        assert stake == HOST_INITIAL_STAKE

    def test_get_host_failed_task_penalty(
        self,
        active_actor,
        HOST_FAILED_TASK_PENALTY
    ):
        penalty = active_actor.get_host_failed_task_penalty()
        assert penalty == HOST_FAILED_TASK_PENALTY

    # tower tests
    def test_get_tower_initial_stake(
        self,
        active_actor,
        TOWER_INITIAL_STAKE
    ):
        stake = active_actor.get_tower_initial_stake()
        assert stake == TOWER_INITIAL_STAKE

    def test_get_tower_failed_task_penalty(
        self,
        active_actor,
        TOWER_FAILED_TASK_PENALTY
    ):
        penalty = active_actor.get_tower_failed_task_penalty()
        assert penalty == TOWER_FAILED_TASK_PENALTY

    def test_get_tower_host_request_fee(
        self,
        active_actor,
        TOWER_HOST_REQUEST_FEE
    ):
        fee = active_actor.get_tower_host_request_fee()
        assert fee == TOWER_HOST_REQUEST_FEE

    # task tests
    def test_get_task_addition_fee(
        self,
        active_actor,
        TASK_ADDITION_FEE
    ):
        fee = active_actor.get_task_addition_fee()
        assert fee == TASK_ADDITION_FEE

    # test the function on the fill environment
