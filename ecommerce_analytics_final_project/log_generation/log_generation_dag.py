from datetime import timedelta

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

args = {
    'owner': 'ec2-user',
    'start_date': airflow.utils.dates.days_ago(2),
}

dag = DAG(
    dag_id='log_generation_pipeline',
    default_args=args,
    schedule_interval=None,
    concurrency=1,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=60),
)

init = DummyOperator(
    task_id='start',
    dag=dag,
)

# create logs for searches
search_creation_task = BashOperator(
    task_id='searches_log_creation',
    bash_command='cd ~/code && python3 fake_log_gen_search.py -n 100 -o LOG && mv *.log ~/searches',
    dag=dag,
)


# create logs for orders
order_creation_task = BashOperator(
    task_id='orders_log_creation',
    bash_command='cd ~/code && python3 fake_log_gen_orders.py -n 100 -o LOG && mv *.log ~/orders',
    dag=dag,
)

# create logs for members
member_creation_creation_task = BashOperator(
    task_id='member_access_log_creation',
    bash_command='cd ~/code && python3 fake_log_gen_login.py -n 100 -o LOG && mv *.log ~/members',
    dag=dag,
)


final_stage = DummyOperator(
    task_id = 'end',
    dag = dag,
)

init.set_downstream(search_creation_task)
search_creation_task.set_downstream(order_creation_task)
order_creation_task.set_downstream(member_creation_creation_task)
member_creation_creation_task.set_downstream(final_stage)