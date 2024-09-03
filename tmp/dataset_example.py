import ssl
import urllib.request
# SSL 인증서 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

import vega_datasets as ds
ds.data('weball26')

ds.data('us-employment')
ds.data('unemployment-across-industries')



for i in ds.data.list_datasets():
    try:
        df = ds.data(i)
        print(f"{i} : {df.shape}")
        print(df.head())
    except:
        print(i)
        pass

