import numpy as np
import pandas as pd


def get_close(ticker):
    df = pd.read_csv(f'./prices/{ticker}.csv', index_col=0, parse_dates=True)
    close = df['Adj Close']
    return close


def run_stats(ticker='SPY', ttm=10,
              exp_r_annl = 0.16,
              call_core=0.7, put_core=0.7,
              call_wing=0.7, put_wing=0.7, ):
    px_0 = get_close(ticker).rename(f'{ticker}_0')
    std_0 = get_close('^VIX').loc[px_0.index[0]:].rename(f'{ticker}_std_0')/100
    mu = exp_r_annl*ttm/252
    sigma_0 = std_0*np.sqrt(ttm/252)
    expr_0 = mu + 0.5*sigma_0**2
    px_t = px_0.shift(-ttm)
    Ks_0 = pd.DataFrame({
        'A': px_0 * np.exp(expr_0 - sigma_0*(put_core+put_wing)),
        'B': px_0 * np.exp(expr_0 - sigma_0*(put_core)),
        'C': px_0 * np.exp(expr_0 + sigma_0*(call_core)),
        'D': px_0 * np.exp(expr_0 + sigma_0*(call_core+call_wing)),
    })
    regs_t = pd.DataFrame({
        'A':                       (px_t < Ks_0['A']),
        'B': (px_t >= Ks_0['A']) & (px_t < Ks_0['B']),
        'C': (px_t >= Ks_0['B']) & (px_t < Ks_0['C']),
        'D': (px_t >= Ks_0['C']) & (px_t < Ks_0['D']),
        'E': (px_t >= Ks_0['D']),
    })
    print('Landing Regions:')
    print('| at | count |  prob  |')
    print('-----------------------')
    for region, ser in regs_t.items():
        print(f'|  {region} | {ser.sum():5d} | {ser.sum()/len(ser):6.2%} |')


if __name__ == '__main__':
    run_stats()