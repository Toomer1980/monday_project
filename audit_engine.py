import json
import pandas as pd
import re
import os

def consolidate_financials(ledger_json, relay_log):
    with open(ledger_json, 'r') as f:
        ledger_data = json.load(f)
        df_ledger = pd.DataFrame(ledger_data)
    with open(relay_log, 'r') as f:
        log_content = f.read()
        broadcasts = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) BROADCAST INITIATED: (.*?) HEX_STAMP: (.*)', log_content)
        df_relay = pd.DataFrame(broadcasts, columns=['timestamp', 'type', 'hex_stamp'])
    consolidated = pd.concat([df_ledger, df_relay], ignore_index=True)
    net_flow = consolidated[consolidated['type'].isin(['EXECUTE_TX', 'hardware_allocation', '10,000 BTC SHADOW MANIFEST'])]
    print(net_flow)
    # Export to Invoices
    os.makedirs('Invoices', exist_ok=True)
    net_flow.to_csv('Invoices/audit_report.csv', index=False)
    print('\nAudit report exported to Invoices/audit_report.csv')

if __name__ == '__main__':
    consolidate_financials('sovereign_ledger.json', 'relay_log.txt')
