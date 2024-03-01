class TestMecaTowerClean:
    def test_clean_tower_functions(
        self,
        simple_setup,
        initial_tower
    ):
        _, _, actors = simple_setup
        actors["tower"].register_tower(
            size_limit=initial_tower["sizeLimit"],
            public_connection=initial_tower["publicConnection"],
            fee=initial_tower["fee"],
            fee_type=initial_tower["feeType"],
            initial_deposit=initial_tower["stake"]
        )

        assert actors["tower"].get_tower_size_limit(
            actors["tower"].account.address
        ) == initial_tower["sizeLimit"]
        assert actors["tower"].get_tower_public_uri(
            actors["tower"].account.address
        ) == initial_tower["publicConnection"]
        assert actors["tower"].get_tower_stake(
            actors["tower"].account.address
        ) == initial_tower["stake"]
        assert actors["tower"].get_tower_fee(
            tower_address=actors["tower"].account.address,
            size=10,
            block_timeout_limit=10
        ) == initial_tower["fee"]

        new_public_connection = "http://localhost:8081"
        actors["tower"].update_tower_public_connection(
            new_public_connection=new_public_connection
        )
        assert actors["tower"].get_tower_public_uri(
            actors["tower"].account.address
        ) == new_public_connection

        new_fee = 20
        actors["tower"].update_fee(
            new_fee=new_fee,
            new_fee_type=0
        )
        assert actors["tower"].get_tower_fee(
            tower_address=actors["tower"].account.address,
            size=10,
            block_timeout_limit=10
        ) == new_fee

        actors["tower"].update_tower_size_limit(
            new_size_limit=0
        )
        assert actors["tower"].get_tower_size_limit(
            actors["tower"].account.address
        ) == 0

        actors["tower"].delete_tower()


class TestMecaTowerRegister:
    def test_register_for_tower(
        self,
        register_setup
    ):
        _, _, actors = register_setup

        assert actors["host"].is_registered()

        tower_hosts = actors["tower"].get_my_hosts()

        assert len(tower_hosts) == 0

        actors["host"].register_for_tower(
            tower_address=actors["tower"].account.address
        )

        pending_hosts = actors["tower"].get_pending_hosts()

        assert len(pending_hosts) == 1
        assert pending_hosts[0] == actors["host"].account.address

        actors["tower"].reject_host(
            host_address=actors["host"].account.address
        )

        pending_hosts = actors["tower"].get_pending_hosts()

        assert len(pending_hosts) == 0

        actors["host"].register_for_tower(
            tower_address=actors["tower"].account.address
        )

        pending_hosts = actors["tower"].get_pending_hosts()

        assert len(pending_hosts) == 1
        assert pending_hosts[0] == actors["host"].account.address

        actors["tower"].accept_host(
            host_address=actors["host"].account.address
        )

        pending_hosts = actors["tower"].get_pending_hosts()

        assert len(pending_hosts) == 0

        tower_hosts = actors["tower"].get_my_hosts()

        assert len(tower_hosts) == 1
        assert tower_hosts[0] == actors["host"].account.address
