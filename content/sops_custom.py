# Your own SOPs and catalog rows. This file runs after the built-in SOPs, so S(), SOPS and CAT already exist.
# S(id, category, title, purpose, level(1-3), concept-part-number, 'Portal>Path>Here',
#   'step 1|step 2', 'validation 1|validation 2', 'rollback 1', 'symptom => fix|symptom => fix',
#   'path/on/learn.microsoft.com (after /en-us/azure/)', cmd=[('CLI','az ...','what it does')],
#   sec='security note|another', prod='production note|another')
CUSTOM = [
    # S('ddos2','Security','Example SOP','What it achieves.',2,8,'Service>Create',
    #   'Open the service|Select Create','Resource shows Succeeded','Delete the resource','Error => Fix','key-vault/general/overview'),
]
SOPS += CUSTOM
# Catalog rows: 'Service name|Category|concept part number|sop id' (sop id optional), one per line.
CAT += ''
