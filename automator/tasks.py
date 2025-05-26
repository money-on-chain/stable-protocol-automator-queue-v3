import decimal
from web3 import Web3
from web3.exceptions import Web3RPCError
import datetime

from .contracts import MocMultiCollateralGuard, MocCACoinbase, MocCARC20, PriceProvider

from .base.main import ConnectionHelperBase
from .tasks_manager import PendingTransactionsTasksManager, on_pending_transactions
from .logger import log


__VERSION__ = '1.0.6'


log.info("Starting Stable Protocol Queue Automator version {0}".format(__VERSION__))


class Automator(PendingTransactionsTasksManager):

    def __init__(self,
                 config,
                 connection_helper,
                 contracts_loaded
                 ):
        self.config = config
        self.connection_helper = connection_helper
        self.contracts_loaded = contracts_loaded

        # init PendingTransactionsTasksManager
        super().__init__(self.config,
                         self.connection_helper,
                         self.contracts_loaded)

    def info_tx(self):

        web3 = self.connection_helper.connection_manager.web3

        nonce = web3.eth.get_transaction_count(
            self.connection_helper.connection_manager.accounts[0].address, "pending")

        # get gas price from node
        node_gas_price = decimal.Decimal(Web3.from_wei(web3.eth.gas_price, 'ether'))

        # Multiply factor of the using gas price
        calculated_gas_price = node_gas_price * decimal.Decimal(self.config['gas_price_multiply_factor'])
        max_fee_per_gas = None
        if max_fee_per_gas in self.config:
            max_fee_per_gas = self.config['max_fee_per_gas']
        max_priority_fee_per_gas = None
        if max_priority_fee_per_gas in self.config:
            max_priority_fee_per_gas = self.config['max_priority_fee_per_gas']

        return dict(
            nonce=nonce,
            calculated_gas_price=calculated_gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas
        )

    def is_valid_tp_price(self):
        valid = True
        for pp in self.contracts_loaded["PriceProviders"]:
            price_item = pp.peek()
            valid = price_item[1]
            if not valid:
                break
        return valid

    def is_valid_ac_coinbase_price(self):
        valid = True
        for pp in self.contracts_loaded["PriceProvidersACCoinbase"]:
            price_item = pp.peek()
            valid = price_item[1]
            if not valid:
                break
        return valid

    @on_pending_transactions
    def execute(self, task=None, global_manager=None, task_result=None):

        # If ready to execute the queue?
        ready_to_execute = self.contracts_loaded["MocMultiCollateralGuard"].ready_to_execute()
        if ready_to_execute:

            # return if there are pending transactions
            if task_result.get('pending_transactions', None):
                return task_result

            # check if is valid price before send
            if not self.is_valid_tp_price():
                log.error("Task :: {0} :: Error not valid TP price provider!".format(task.task_name))
                return

            info_transaction = self.info_tx()

            try:
                tx_hash = self.contracts_loaded["MocMultiCollateralGuard"].execute(
                    self.config['tasks']['execute']['fee_recipient'],
                    gas_limit=self.config['tasks']['execute']['gas_limit'],
                    gas_price=int(info_transaction['calculated_gas_price'] * 10 ** 18),
                    max_fee_per_gas=info_transaction['max_fee_per_gas'],
                    max_priority_fee_per_gas=info_transaction['max_priority_fee_per_gas'],
                    nonce=info_transaction['nonce']
                )
            except ValueError as err:
                log.error("Task :: {0} :: Error sending transaction! \n {1}".format(task.task_name, err))
                return task_result

            if tx_hash:
                new_tx = dict()
                new_tx['hash'] = tx_hash
                new_tx['timestamp'] = datetime.datetime.now()
                new_tx['gas_price'] = info_transaction['calculated_gas_price']
                new_tx['nonce'] = info_transaction['nonce']
                new_tx['timeout'] = self.config['tasks']['execute']['wait_timeout']
                task_result['pending_transactions'].append(new_tx)

                log.info("Task :: {0} :: Sending TX :: Hash: [{1}] Nonce: [{2}] Gas Price: [{3}]".format(
                    task.task_name, Web3.to_hex(new_tx['hash']), new_tx['nonce'], int(info_transaction['calculated_gas_price'] * 10 ** 18)))

        else:
            log.info("Task :: {0} :: No!".format(task.task_name))

        return task_result

    @on_pending_transactions
    def execute_micro_liquidation(self, bucket, task=None, global_manager=None, task_result=None):

        # If ready to execute the micro liquidation?
        ready_to_execute = self.contracts_loaded["MocMultiCollateralGuard"].is_micro_liquidation_available(bucket)
        if ready_to_execute:

            # return if there are pending transactions
            if task_result.get('pending_transactions', None):
                return task_result

            # check if is valid price before send
            if not self.is_valid_tp_price():
                log.error("Task :: {0} :: Error not valid TP price provider!".format(task.task_name))
                return

            info_transaction = self.info_tx()

            try:
                tx_hash = self.contracts_loaded["MocMultiCollateralGuard"].execute_micro_liquidation(
                    bucket,
                    self.config['tasks']['execute_micro_liquidation']['fee_recipient'],
                    gas_limit=self.config['tasks']['execute_micro_liquidation']['gas_limit'],
                    gas_price=int(info_transaction['calculated_gas_price'] * 10 ** 18),
                    max_fee_per_gas=info_transaction['max_fee_per_gas'],
                    max_priority_fee_per_gas=info_transaction['max_priority_fee_per_gas'],
                    nonce=info_transaction['nonce']
                )
            except ValueError as err:
                log.error("Task :: {0} :: Error sending transaction! \n {1}".format(task.task_name, err))
                return task_result

            if tx_hash:
                new_tx = dict()
                new_tx['hash'] = tx_hash
                new_tx['timestamp'] = datetime.datetime.now()
                new_tx['gas_price'] = info_transaction['calculated_gas_price']
                new_tx['nonce'] = info_transaction['nonce']
                new_tx['timeout'] = self.config['tasks']['execute_micro_liquidation']['wait_timeout']
                task_result['pending_transactions'].append(new_tx)

                log.info("Task :: {0} :: Sending TX :: Hash: [{1}] Nonce: [{2}] Gas Price: [{3}]".format(
                    task.task_name, Web3.to_hex(new_tx['hash']), new_tx['nonce'], int(info_transaction['calculated_gas_price'] * 10 ** 18)))

        else:
            log.info("Task :: {0} :: No!".format(task.task_name))

        return task_result

    @on_pending_transactions
    def execute_liquidation(self, bucket, task=None, global_manager=None, task_result=None):

        # If ready to execute the micro liquidation?
        ready_to_execute = self.contracts_loaded["MocMultiCollateralGuard"].is_liquidation_available(bucket)
        if ready_to_execute:

            # return if there are pending transactions
            if task_result.get('pending_transactions', None):
                return task_result

            # check if is valid price before send
            if not self.is_valid_tp_price():
                log.error("Task :: {0} :: Error not valid TP price provider!".format(task.task_name))
                return

            # check if is valid ac coinbase price before send
            if not self.is_valid_ac_coinbase_price():
                log.error("Task :: {0} :: Error not valid AC Coinbase price provider!".format(task.task_name))
                return

            info_transaction = self.info_tx()

            try:
                tx_hash = self.contracts_loaded["MocMultiCollateralGuard"].execute_liquidation(
                    bucket,
                    self.config['tasks']['execute_liquidation']['fee_recipient'],
                    gas_limit=self.config['tasks']['execute_liquidation']['gas_limit'],
                    gas_price=int(info_transaction['calculated_gas_price'] * 10 ** 18),
                    max_fee_per_gas=info_transaction['max_fee_per_gas'],
                    max_priority_fee_per_gas=info_transaction['max_priority_fee_per_gas'],
                    nonce=info_transaction['nonce']
                )
            except ValueError as err:
                log.error("Task :: {0} :: Error sending transaction! \n {1}".format(task.task_name, err))
                return task_result

            if tx_hash:
                new_tx = dict()
                new_tx['hash'] = tx_hash
                new_tx['timestamp'] = datetime.datetime.now()
                new_tx['gas_price'] = info_transaction['calculated_gas_price']
                new_tx['nonce'] = info_transaction['nonce']
                new_tx['timeout'] = self.config['tasks']['execute_liquidation']['wait_timeout']
                task_result['pending_transactions'].append(new_tx)

                log.info("Task :: {0} :: Sending TX :: Hash: [{1}] Nonce: [{2}] Gas Price: [{3}]".format(
                    task.task_name, Web3.to_hex(new_tx['hash']), new_tx['nonce'], int(info_transaction['calculated_gas_price'] * 10 ** 18)))

        else:
            log.info("Task :: {0} :: No!".format(task.task_name))

        return task_result


class AutomatorTasks(Automator):

    def __init__(self, config):

        self.config = config
        self.connection_helper = ConnectionHelperBase(config)

        self.contracts_loaded = dict()
        self.contracts_addresses = dict()
        self.moc_buckets_addresses = []

        # contract addresses
        self.load_contracts()

        # init automator
        super().__init__(self.config,
                         self.connection_helper,
                         self.contracts_loaded)

        # Add tasks
        self.schedule_tasks()

    def load_contracts(self):
        """ Get contract address to use later """

        log.info("Getting addresses from Main Contract...")

        log.info("MocMultiCollateralGuard using address: %s" % self.config['addresses']['MocMultiCollateralGuard'])
        # MocMultiCollateralGuard
        self.contracts_loaded["MocMultiCollateralGuard"] = MocMultiCollateralGuard(
            self.connection_helper.connection_manager,
            contract_address=self.config['addresses']['MocMultiCollateralGuard'])
        self.contracts_addresses['MocMultiCollateralGuard'] = self.contracts_loaded["MocMultiCollateralGuard"].address().lower()

        # Reading MoC Buckets from Multi collateral Guard
        self.moc_buckets_addresses = []
        self.contracts_loaded['Moc'] = []

        for ca_index, ca in enumerate(self.config['collateral']):
            try:
                moc_bucket_address = self.contracts_loaded["MocMultiCollateralGuard"].buckets(ca_index)
            except Web3RPCError:
                continue

            contract_interface = MocCACoinbase
            if ca['type'] == 'rc20':
                contract_interface = MocCARC20

            log.info("MoC Bucket ({0}) using address: {1}".format(ca['name'], moc_bucket_address))

            moc_bucket = contract_interface(
                self.connection_helper.connection_manager,
                contract_address=moc_bucket_address)

            self.contracts_loaded['Moc'].append(moc_bucket)
            self.moc_buckets_addresses.append(moc_bucket_address)

        # Get TP Price provider... in multi-collateral we have the assumption that all collateral
        # have the same TPs, this why only watch the first collateral only

        price_providers = []
        bucket_index = 0
        for tp_i, tp in enumerate(self.config['pegged']):
            try:
                tp_address = self.contracts_loaded["Moc"][bucket_index].tp_tokens(tp_i)
            except Web3RPCError:
                continue
            if not tp_address:
                break
            tp_index = self.contracts_loaded["Moc"][bucket_index].pegged_token_index(tp_address)
            # result: tp_index = [index, enabled]
            if not tp_index:
                break
            tp_item = self.contracts_loaded["Moc"][bucket_index].peg_container(tp_index[0])
            # result: tp_item = [index, price provider]
            price_providers.append(tp_item[1])

        # load TP price providers
        self.contracts_loaded["PriceProviders"] = []
        for pp_address_index, pp_address in enumerate(price_providers):
            log.info("Price Provider TP ({0}) using address: {1}".format(
                self.config['pegged'][pp_address_index]['name'], pp_address))
            pp = PriceProvider(
                self.connection_helper.connection_manager,
                contract_address=pp_address)
            self.contracts_loaded["PriceProviders"].append(pp)

        # Get AC Coinbase price provider if need it
        self.contracts_loaded["PriceProvidersACCoinbase"] = []
        for moc_bucket_addr_index, moc_bucket_addr in enumerate(self.moc_buckets_addresses):
            ac_coinbase_pp_address = self.contracts_loaded["MocMultiCollateralGuard"].ac_coinbase_price_provider(moc_bucket_addr)
            if ac_coinbase_pp_address != "0x0000000000000000000000000000000000000000":
                log.info("Price Provider AC Coinbase ({0}) using address: {1}".format(
                    self.config['collateral'][moc_bucket_addr_index]['name'], ac_coinbase_pp_address))
                pp = PriceProvider(
                    self.connection_helper.connection_manager,
                    contract_address=ac_coinbase_pp_address)
                self.contracts_loaded["PriceProvidersACCoinbase"].append(pp)

    def schedule_tasks(self):

        log.info("Starting adding tasks...")

        # set max workers
        self.max_workers = 1

        if 'execute' in self.config['tasks']:
            log.info("Jobs add: 1. Execute Queue")
            interval = self.config['tasks']['execute']['interval']
            self.add_task(self.execute,
                          args=[],
                          wait=interval,
                          timeout=180,
                          task_name='1. Execute Queue')

        # Execute micro liquidation
        if 'execute_micro_liquidation' in self.config['tasks']:
            count = 0
            for moc_bucket_addr in self.moc_buckets_addresses:
                log.info("Jobs add: 2. Execute micro liquidation: ({0}) {1}".format(
                    self.config['collateral'][count]['name'], moc_bucket_addr)
                )
                interval = self.config['tasks']['execute_micro_liquidation']['interval']
                self.add_task(self.execute_micro_liquidation,
                              args=[moc_bucket_addr],
                              wait=interval,
                              timeout=180,
                              task_name="2. Execute micro liquidation: ({0}) {1}".format(
                                  self.config['collateral'][count]['name'], moc_bucket_addr)
                              )
                count += 1

        # Execute liquidation
        if 'execute_liquidation' in self.config['tasks']:
            count = 0
            for moc_bucket_addr in self.moc_buckets_addresses:
                log.info("Jobs add: 3. Execute liquidation: ({0}) {1}".format(
                    self.config['collateral'][count]['name'], moc_bucket_addr)
                )
                interval = self.config['tasks']['execute_liquidation']['interval']
                self.add_task(self.execute_liquidation,
                              args=[moc_bucket_addr],
                              wait=interval,
                              timeout=180,
                              task_name="2. Execute liquidation: ({0}) {1}".format(
                                  self.config['collateral'][count]['name'], moc_bucket_addr)
                              )
                count += 1

        # Set max workers
        self.max_tasks = len(self.tasks)
