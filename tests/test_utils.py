import web3
from eth_account import Account


class TestGanache:
    def test_accounts(
        self,
        INITIAL_BALANCE,
        accounts,
        clean_setup
    ):
        balance_dao = clean_setup.eth.get_balance(
            Account.from_key(
                accounts["meca_dao"]["private_key"]
            ).address
        )
        balance_host = clean_setup.eth.get_balance(
            Account.from_key(
                accounts["meca_host"]["private_key"]
            ).address
        )
        balance_user = clean_setup.eth.get_balance(
            Account.from_key(
                accounts["meca_user"]["private_key"]
            ).address
        )
        balance_task = clean_setup.eth.get_balance(
            Account.from_key(
                accounts["meca_task"]["private_key"]
            ).address
        )
        balance_tower = clean_setup.eth.get_balance(
            Account.from_key(
                accounts["meca_tower"]["private_key"]
            ).address
        )
        wei_initial_deposit = web3.Web3.to_wei(INITIAL_BALANCE, "ether")
        assert balance_dao == wei_initial_deposit
        assert balance_host == wei_initial_deposit
        assert balance_user == wei_initial_deposit
        assert balance_task == wei_initial_deposit
        assert balance_tower == wei_initial_deposit
        assert clean_setup.eth.get_block("latest")["number"] == 0
