import os
OKAREO_API_KEY = os.environ.get('OKAREO_API_KEY', "<YOUR_OKAREO_API_KEY>")
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', "<YOUR_OPENAI_API_KEY>")

# Simple summarization prompt using OpenAI'a GPT 3.5 Turbo model
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)
def get_turbo_summary(messages, model="gpt-3.5-turbo",
  temperature=0, max_tokens=500):
  response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
  )
  return response.choices[0].message.content
USER_PROMPT_TEMPLATE = "{input}"
SUMMARIZATION_CONTEXT_TEMPLATE = """
You will be provided with text.
Summarize the text in 1 simple sentence.
"""

# Evaluate the scenario and model combination and then get a link to the results on Okareo
import random
import string

import tempfile
from okareo import Okareo
from okareo.model_under_test import OpenAIModel
from okareo_api_client.models.test_run_type import TestRunType
okareo = Okareo(OKAREO_API_KEY)
random_string = ''.join(random.choices(string.ascii_letters, k=5))
mut_name = f"OpenAI Summarization Model - {random_string}"
eval_name = f"Summarization Run - {random_string}"
# Register the model to use in the test run
model_under_test = okareo.register_model(
    name=mut_name,
    model=OpenAIModel(
        model_id="gpt-3.5-turbo",
        temperature=0,
        system_prompt_template=SUMMARIZATION_CONTEXT_TEMPLATE,
        user_prompt_template=USER_PROMPT_TEMPLATE,
    ),
)
# Create a scenario to evaluate the model with
# Get jsonl file from Okareo's SDK repo
webbizz_articles = os.popen('curl https://raw.githubusercontent.com/okareo-ai/okareo-python-sdk/main/examples/webbizz_10_articles.jsonl').read()
temp_dir = tempfile.gettempdir()
file_path = os.path.join(temp_dir, "webbizz_10_articles.jsonl")
with open(file_path, "w+") as file:
    lines = webbizz_articles.split('\n')
    # Use the first 3 json objects to make a scenario set with 3 scenarios
    for i in range(3):
        file.write(f"{lines[i]}\n")
scenario = okareo.upload_scenario_set(file_path=file_path, scenario_name="Webbizz Articles Scenario15")
# make sure to clean up tmp file
os.remove(file_path)
# Run the evaluation
evaluation = model_under_test.run_test(
    name=eval_name,
    scenario=scenario,
    api_key=OPENAI_API_KEY,
    test_run_type=TestRunType.NL_GENERATION,
    calculate_metrics=True,
    checks=['coherence_summary', 'consistency_summary', 'fluency_summary', 'relevance_summary']
)
print(f"See results in Okareo: {evaluation.app_link}")
