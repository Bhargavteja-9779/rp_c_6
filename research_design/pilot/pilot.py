# EXPLORATORY PILOT (not confirmatory evidence): seen vs novel coverage of split CP
import numpy as np, pandas as pd, sys
from sklearn.datasets import fetch_openml
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.model_selection import train_test_split
alpha=0.1
for did in [int(a) for a in sys.argv[1:]]:
    b=fetch_openml(data_id=did,parser='pandas',as_frame=True,data_home='/home/user/rp_c_6/.openml_cache')
    X=b.data.copy(); y=pd.factorize(b.target)[0]
    cat=X.select_dtypes(exclude='number').columns
    if len(cat): X[cat]=OrdinalEncoder().fit_transform(X[cat].astype(str))
    X=X.astype(float).fillna(-999).values
    key=pd.util.hash_pandas_object(pd.DataFrame(X),index=False).values
    res=[]
    for seed in range(5):
        idx=np.arange(len(y)); tr,rest=train_test_split(idx,test_size=0.4,random_state=seed); ca,te=train_test_split(rest,test_size=0.5,random_state=seed)
        seen=np.isin(key,key[tr])
        for name,m in [('LR',make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000))),('RF',RandomForestClassifier(300,n_jobs=4,random_state=seed))]:
            m.fit(X[tr],y[tr]); P=lambda i: m.predict_proba(X[i])
            pc,pt=P(ca),P(te); K=pc.shape[1]
            s=1-pc[np.arange(len(ca)),y[ca]]; n=len(s); q=np.quantile(s,min(1,np.ceil((n+1)*(1-alpha))/n),method='higher')
            cov=(1-pt[np.arange(len(te)),y[te]])<=q
            # mondrian by novelty
            out={}
            for g in (True,False):
                sg=s[seen[ca]==g]; ng=len(sg)
                qg=np.inf if (ng+1)*(1-alpha)>ng else np.quantile(sg,np.ceil((ng+1)*(1-alpha))/ng,method='higher')
                out[g]=(1-pt[np.arange(len(te)),y[te]])<=qg
            covm=np.where(seen[te],out[True],out[False])
            res.append(dict(model=name,seed=seed,pi_test=seen[te].mean(),cov=cov.mean(),cov_seen=cov[seen[te]].mean(),cov_novel=cov[~seen[te]].mean(),mond_novel=covm[~seen[te]].mean(),mond_all=covm.mean()))
    r=pd.DataFrame(res).groupby('model').mean(numeric_only=True).round(3)
    print(did,b.details['name'],len(y),'dup-rate',round(pd.Series(key).duplicated(keep=False).mean(),3)); print(r)
