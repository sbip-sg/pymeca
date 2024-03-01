import pytest
import pymeca.dao


# test MecaDAOOwner
@pytest.fixture(scope="class")
def dao_owner(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.dao.MecaDAOOwner(
        w3=w3,
        private_key=accounts["meca_dao"]["private_key"],
        contract_address=addresses["dao_contract_address"]
    )


# test MecaSchedulerOwner
@pytest.fixture(scope="class")
def scheduler_owner(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.dao.MecaSchedulerOwner(
        w3=w3,
        private_key=accounts["meca_dao"]["private_key"],
        contract_address=addresses["scheduler_contract_address"]
    )


# test MecaTowerContractOwner
@pytest.fixture(scope="class")
def tower_contract_owner(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.dao.MecaTowerContractOwner(
        w3=w3,
        private_key=accounts["meca_dao"]["private_key"],
        contract_address=addresses["tower_contract_address"]
    )


# test MecaHostContractOwner
@pytest.fixture(scope="class")
def host_contract_owner(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.dao.MecaHostContractOwner(
        w3=w3,
        private_key=accounts["meca_dao"]["private_key"],
        contract_address=addresses["host_contract_address"]
    )


# test MecaTaskContractOwner
@pytest.fixture(scope="class")
def task_contract_owner(
    accounts,
    simple_setup
):
    w3, addresses, _ = simple_setup
    return pymeca.dao.MecaTaskContractOwner(
        w3=w3,
        private_key=accounts["meca_dao"]["private_key"],
        contract_address=addresses["task_contract_address"]
    )


class TestDaoGetters:
    # dao tests
    def test_get_scheduler(
        self,
        dao_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        scheduler_contract_address = addresses["scheduler_contract_address"]
        address = dao_owner.get_scheduler_address()
        assert address == scheduler_contract_address

    # scheduler tests
    def test_get_flag(
        self,
        scheduler_owner
    ):
        flag = scheduler_owner.get_flag()
        assert flag is True

    def test_get_host_contract_address(
        self,
        scheduler_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        host_contract_address = addresses["host_contract_address"]
        address = scheduler_owner.get_host_contract_address()
        assert address == host_contract_address

    def test_get_tower_contract_address(
        self,
        scheduler_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        tower_contract_address = addresses["tower_contract_address"]
        address = scheduler_owner.get_tower_contract_address()
        assert address == tower_contract_address

    def test_get_task_contract_address(
        self,
        scheduler_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        task_contract_address = addresses["task_contract_address"]
        address = scheduler_owner.get_task_contract_address()
        assert address == task_contract_address

    # tower tests
    def test_get_tower_scheduler_address(
        self,
        tower_contract_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        scheduler_contract_address = addresses["scheduler_contract_address"]
        address = tower_contract_owner.get_scheduler_address()
        assert address == scheduler_contract_address

    # host tests
    def test_get_host_scheduler_address(
        self,
        host_contract_owner,
        simple_setup
    ):
        _, addresses, _ = simple_setup
        scheduler_contract_address = addresses["scheduler_contract_address"]
        address = host_contract_owner.get_scheduler_address()
        assert address == scheduler_contract_address

    # task tests


class TestDaoSetters:
    # dao tests
    def test_set_scheduler(
        self,
        dao_owner
    ):
        new_scheduler_address = "0x" + "1" * 40
        dao_owner.set_scheduler(
            contract_address=new_scheduler_address
        )
        address = dao_owner.get_scheduler_address()
        assert address == new_scheduler_address

    # scheduler tests
    def test_set_flag(
        self,
        scheduler_owner
    ):
        scheduler_owner.set_flag(
            flag=False
        )
        flag = scheduler_owner.get_flag()
        assert flag is False

    def test_set_host_contract_address(
        self,
        scheduler_owner
    ):
        new_host_contract_address = "0x" + "2" * 40
        scheduler_owner.set_host_contract(
            contract_address=new_host_contract_address
        )
        address = scheduler_owner.get_host_contract_address()
        assert address == new_host_contract_address

    def test_set_tower_contract_address(
        self,
        scheduler_owner
    ):
        new_tower_contract_address = "0x" + "3" * 40
        scheduler_owner.set_tower_contract(
            contract_address=new_tower_contract_address
        )
        address = scheduler_owner.get_tower_contract_address()
        assert address == new_tower_contract_address

    def test_set_task_contract_address(
        self,
        scheduler_owner
    ):
        new_task_contract_address = "0x" + "4" * 40
        scheduler_owner.set_task_contract(
            contract_address=new_task_contract_address
        )
        address = scheduler_owner.get_task_contract_address()
        assert address == new_task_contract_address

    # tower tests
    def test_set_tower_scheduler_address(
        self,
        tower_contract_owner
    ):
        new_scheduler_address = "0x" + "5" * 40
        tower_contract_owner.set_scheduler(
            contract_address=new_scheduler_address
        )
        address = tower_contract_owner.get_scheduler_address()
        assert address == new_scheduler_address

    # host tests
    def test_set_host_scheduler_address(
        self,
        host_contract_owner
    ):
        new_scheduler_address = "0x" + "6" * 40
        host_contract_owner.set_scheduler(
            contract_address=new_scheduler_address
        )
        address = host_contract_owner.get_scheduler_address()
        assert address == new_scheduler_address

    # task tests
