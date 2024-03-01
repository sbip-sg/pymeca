import web3
import logging
import pymeca.pymeca
import pymeca.utils

logger = logging.getLogger(__name__)


class MecaTower(pymeca.pymeca.MecaActiveActor):
    def __init__(
        self,
        w3: web3.Web3,
        private_key: str,
        dao_contract_address: str
    ) -> None:
        super().__init__(
            w3=w3,
            private_key=private_key,
            dao_contract_address=dao_contract_address
        )

    def register_tower(
        self,
        size_limit: int,
        public_connection: str,
        fee: int,
        fee_type: int,
        initial_deposit: int
    ) -> bool:
        r"""
        Register tower
        """
        if initial_deposit < self.get_tower_initial_stake():
            raise ValueError(
                "The initial deposit is less than the minimum deposit"
            )

        transaction = self.get_tower_contract().functions.registerAsTower(
            sizeLimit=size_limit,
            publicConnection=public_connection,
            fee=fee,
            feeType=fee_type
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            ),
            "value": initial_deposit
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_tower_size_limit(
        self,
        new_size_limit: int
    ) -> bool:
        r"""
        Update tower size limit
        """
        transaction = self.get_tower_contract().functions.updateSizeLimit(
            newSizeLimit=new_size_limit
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_tower_public_connection(
        self,
        new_public_connection: str
    ) -> bool:
        r"""
        Update tower public connection
        """
        transaction = self.get_tower_contract(
        ).functions.updatePublicConnection(
            newPublicConnection=new_public_connection
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def update_fee(
        self,
        new_fee_type: int,
        new_fee: int
    ) -> bool:
        r"""
        Update fee
        """
        transaction = self.get_tower_contract().functions.updateFee(
            newFee=new_fee,
            newFeeType=new_fee_type
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def delete_tower(
        self
    ) -> bool:
        r"""
        Delete tower
        """
        transaction = self.get_tower_contract(
        ).functions.deleteTower().build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def get_pending_hosts(
        self
    ) -> list:
        r"""
        Get pending hosts
        """
        return self.get_tower_pending_hosts(
            tower_address=self.account.address
        )

    def accept_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Accept host
        """
        transaction = self.get_tower_contract().functions.acceptHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def reject_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Reject host
        """
        transaction = self.get_tower_contract().functions.rejectHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1

    def get_my_hosts(
        self
    ) -> list:
        r"""
        Get my hosts
        """
        return self.get_tower_hosts(
            tower_address=self.account.address
        )

    def delete_host(
        self,
        host_address: str
    ) -> bool:
        r"""
        Delete host
        """
        transaction = self.get_tower_contract().functions.deleteHost(
            hostAddress=host_address
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.w3.eth.get_transaction_count(
                self.account.address
            )
        })

        tx_receipt = self._execute_transaction(transaction)

        return tx_receipt.status == 1
