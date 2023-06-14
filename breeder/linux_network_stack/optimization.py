
def objective(trial, identifier):

###--- definition coroutines ---###
### We have to keep to coroutines in the objective function,
### otherwise the workers do not know about those until we preinstall those.
    {% macro local_coroutines_include() %}{% include 'nats_coroutines.py' %}{% endmacro %}
    {{ local_coroutines_include()|indent }} # default is indent of 4 spaces!
###--- end coroutines ---###

    import logging
    logger = logging.getLogger('objective')
    logger.setLevel(logging.DEBUG)

    logger.warning('entering')

    # Compiling settings for effectuation
    settings = []
    for setting_name, setting_config in config.get('settings').get('sysctl').items():
        constraints = setting_config.get('constraints')
        step_width = setting_config.get('step')
        suggested_value = trial.suggest_int(setting_name, constraints.get('lower') , constraints.get('upper'), step_width)
        if setting_name in ['net.ipv4.tcp_rmem', 'net.ipv4.tcp_wmem']:
            settings.append(f"sudo sysctl -w {setting_name}='4096 131072 {suggested_value}';")
        else:
            settings.append(f"sudo sysctl -w {setting_name}='{suggested_value}';")
    settings = '\n'.join(settings)

    logger.warning('doing effectuation')
    settings_data = dict(settings=settings)
    asyncio.run(send_msg_via_nats(subject=f'effectuation_{identifier}', data_dict=settings_data))

    logger.warning('gathering recon')
    metric = json.loads(asyncio.run(receive_msg_via_nat(subject=f'recon_{identifier}')))
    metric_value = metric.get('metric')
    rtt = float(metric_value['tcp_rtt'])
    delivery_rate = float(metric_value['tcp_delivery_rate_bytes'])
    logger.warning(f'metric received {metric_value}')

    logger.warning('Done')

    return rtt, delivery_rate



def create_optimization_dag(dag_id, config, identifier):

    dag = DAG(dag_id,
              default_args=DEFAULTS,
              description='breeder subdag for optimizing \
                    linux network stack dynamics')

    with dag as optimization_dag:

        dump_config = BashOperator(
            task_id='print_config',
            bash_command='echo ${config}',
            env={"config": str(config)},
            dag=optimization_dag,
        )

        ## perform optimiziation run
        @dag.task(task_id="optimization_step")
        def run_optimization():

            with Client(address="godon_dask_scheduler_1:8786") as client:
                # Create a study using Dask-compatible storage
                storage = DaskStorage(InMemoryStorage())
                study = optuna.create_study(directions=["minimize", "maximize"], storage=storage)
                objective_wrapped = lambda trial: objective(trial, identifier)
                # Optimize in parallel on your Dask cluster
                futures = [
                    client.submit(study.optimize, objective_wrapped, n_trials=10, pure=False)
                ]
                wait(futures, timeout=7200)
                print(f"Best params: {study.best_params}")

        optimization_step = run_optimization()

        dump_config >> optimization_step

    return dag
