# @debug
# def _process_cvm_history_file(cvm_file_info):
#     """
#     Process the CVM history file.
#     Args:
#         cvm_file_info (tuple): A tuple containing three elements - name (str), cvm_file (str), and update_time (datetime).
#     Returns:
#         list: A list of lists, where each inner list contains the following elements:
#             - name (str): The name of the file.
#             - kind (str): The kind of file.
#             - sub_kind (str): The sub-kind of file.
#             - cvm_file (str): The file path.
#             - update_time (datetime): The update time.
#             - len(cvm_if_data) (int): The length of cvm_if_data.
#             - partition_cols (str): The partition columns.
#             - _timelapse(start_time) (str): The time taken for the process.
#             - step (str): The current step in the process.
#             - 'SUCCESS' or 'ERROR' (str): Indicates whether the process was successful or encountered an error.
#             - Error message (str): Provides additional information in case of an error.
#     Overview:
#     This function processes a CVM history file. It initializes parameters and variables, reads the metadata of the CVM file,
#     connects to an in-memory SQLite database, writes the CVM data to a staging table in the database, appends the result to the result list,
#     closes the database connection, and finally returns the result list.
#     Note: If any exception occurs during the process, the code handles it by appending an error message to the result list.
#     """
#     result = []
#     start_time = datetime.now()

#     step = 'SETTING UP COMPONENTS'
#     STAGE=sqlite3.connect(':memory:')
#     try:
#         step = 'INITIALIZING PARAMETERS'
#         name, cvm_file, update_time = cvm_file_info

#         step = 'READING CVM FILE METADATA'
#         kind, sub_kind, cvm_if_data, partition_cols = _read_cvm_history_file(
#             source_file=cvm_file, 
#             apply_converters=True,
#             check_header=False
#         )
#         try:
#             target_table = f'cvm_{kind}_{sub_kind}_history_stg'.lower()

#             cvm_if_data['source'] = '.'.join(cvm_file.split(os.path.sep)[-1].split('.')[0:-1])
#             cvm_if_data['timestamp'] = update_time.strftime('%Y-%m-%d %H:%M:%S')

#             step = 'WRITING CVM DATA STAGE'
#             cvm_if_data.to_sql(target_table, index=False, if_exists='append', con=STAGE)

#             result.append([
#                 name, kind, sub_kind, cvm_file, update_time, len(cvm_if_data), partition_cols, 
#                 _timelapse(start_time), step, 'SUCCESS', None
#             ])
#         except Exception as E:
#             result.append([
#                 name, kind, sub_kind, cvm_file, update_time, len(cvm_if_data), partition_cols, 
#                 _timelapse(start_time), step, 'ERROR', f'ERROR: {E}'
#             ])
#     except Exception as E:
#         info = debug_info(E)
#         if len(cvm_file_info) == 3:
#             name, cvm_file, update_time = cvm_file_info
#         else:
#             name, cvm_file, update_time = None, None, None
#         result.append([
#             name, None, None, cvm_file, update_time, None, None, 
#             _timelapse(start_time), step, 'ERROR', f'ERROR {E} ({info}): WITH info={cvm_file_info}'
#         ])
#     finally:
#         STAGE = None

#     return result

# @debug
# def update_cvm_history_data(parallelize=True):
#     """
#     Updates the history data of Comissão de Valores Mobiliários (CVM) files.
#     Parameters:
#     - parallelize (bool, optional): A boolean flag to indicate if the function should be parallelized. Defaults to True.
#     - history_folder (str, optional): The path to the folder that contains the history data. Defaults to None.
#     Returns:
#     - results (list): A list of dictionaries containing the result data of the CVM files processing.
#     Code Overview:
#     The code updates the history data of CVM files. It checks the validity of the history_folder and the possibility
#     of parallel execution. It then connects to an in-memory SQLite database and tries to execute several steps to
#     update the history data. If an error occurs during the execution of the steps, it raises a ValueError with an
#     appropriate error message. Finally, it closes the connection to the SQLite database.
#     """
#     PARALLELIZE = parallelize and os.cpu_count()>1

#     # disabling parallel processing due to errors with sqlite3
#     PARALLELIZE = False

#     step = 'SETUP COMPONENTS'
#     STAGE = sqlite3.connect(':memory:')
#     try:
#         step = 'LOAD CATALOG UPDATES'
#         catalog_updates = pd.read_sql(f'''
#             select * 
#             from {self.CATALOG_JOURNAL} 
#             where active 
#             and last_updated is null 
#                 or last_download > last_updated
#             order by kind, name
#         ''', con=self.CATALOG).to_dict(orient='records')

#         results = []
#         if len(catalog_updates) > 0:
#             step = 'SELECTING FILES TO UPDATE'
#             cvm_files = []
#             for name, mask in [
#                 (u['name'], f"{u['kind'].lower()}.{u['name'].split('.')[0]}.*") for u in catalog_updates
#             ]:
#                 for cvm_file in FU.find(self.HISTORY_FOLDER, mask):
#                     cvm_files += [[name, cvm_file]]

#             if len(cvm_files) == 0:
#                 return []

#             step = 'CHECKING HEADERS'
#             if self._check_cvm_headers_changed(cvm_files=[f[1] for f in cvm_files]):
#                 raise ValueError('Headers Changed! Update not possible.')

#             step = 'UPDATE CVM HISTORY DATA'
#             update_time = datetime.now()

#             cvm_files = [[f[0], f[1], update_time] for f in cvm_files]

#             if PARALLELIZE:
#                 with Pool(os.cpu_count()) as p:
#                     results = p.map(_process_cvm_history_file, cvm_files)
#             else:
#                 for cvm_file in cvm_files:
#                     result = _process_cvm_history_file(cvm_file)
#                     results.append(result)

#             step = 'UPDATE CVM CATALOG JOURNAL: CONSOLIDATING INFO'
#             result_cols = [
#                 'name', 'kind', 'sub_kind', 'cvm_file', 'update_time', 'records', 
#                 'partition_cols', 'timelapse', 'last_step', 'status', 'message'
#             ]
#             result_data = pd.DataFrame(
#                 [r for r in [r[0] for r in results]], columns=result_cols
#             )
#             result_table = 'cvm_update_history_results_stg'
#             result_data.to_sql(result_table, con=STAGE, index=False, if_exists='replace')

#             step = 'UPDATE CVM CATALOG JOURNAL: UPDATING DATA'
#             for name, kind, update_time in pd.read_sql(f'''
#                 with t as (
#                     select name, kind,
#                         sum(case when status='ERROR' then 1 else 0 end) errors, 
#                         sum(case when status='SUCCESS' then 1 else 0 end) successes,
#                         max(update_time) update_time
#                     from {result_table}
#                     group by name, kind
#                 )
#                 select name, kind, update_time
#                 from t
#                 where errors = 0
#                 and successes > 0
#             ''', con=STAGE).to_records(index=False):
#                 _ = self.CATALOG.execute(f'''
#                     update {self.CATALOG_JOURNAL}
#                     set last_updated = '{update_time}',
#                         process = FALSE
#                     where name = '{name}'
#                     and kind = '{kind}';
#                 ''')
#                 sleep(0.5)

#         return results
#     except Exception as E:
#         info = debug_info(E)
#         raise ValueError('Fail to get CVM UPDATE HISTORY DATA Data on step {}: {} ({}) (name={}, file={})'.format(
#             step, E, info, name, cvm_file))
#     finally:
#         STAGE = None


