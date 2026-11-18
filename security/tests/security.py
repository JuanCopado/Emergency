import marshal
import os
import pickle
import requests
import ssl
import subprocess
import yaml

# ruleid: python-dynamic-eval
eval(user_input)
# ruleid: python-dynamic-eval
exec(user_input)
# ok: python-dynamic-eval
int(user_input)

# ruleid: python-shell-execution
subprocess.run(command, shell=True)
# ok: python-shell-execution
subprocess.run(["python", "--version"], shell=False)

# ruleid: python-unsafe-deserialization
pickle.loads(payload)
# ruleid: python-unsafe-deserialization
marshal.loads(payload)
# ok: python-unsafe-deserialization
str(payload)

# ruleid: python-unsafe-yaml
yaml.load(payload, Loader=yaml.Loader)
# ok: python-unsafe-yaml
yaml.load(payload, Loader=yaml.SafeLoader)
# ok: python-unsafe-yaml
yaml.load(payload, Loader=yaml.BaseLoader)
# ok: python-unsafe-yaml
yaml.safe_load(payload)

# ruleid: python-tls-verification-disabled
requests.get(url, verify=False)
# ruleid: python-tls-verification-disabled
ssl._create_unverified_context()
# ok: python-tls-verification-disabled
requests.get(url, verify=True)

# ruleid: python-sql-interpolation
cursor.execute(f"SELECT * FROM records WHERE id = {user_input}")
# ok: python-sql-interpolation
cursor.execute("SELECT * FROM records WHERE id = ?", (user_input,))
