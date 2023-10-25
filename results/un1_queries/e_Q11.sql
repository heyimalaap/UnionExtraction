Select ps_comment, Sum(ps_availqty*ps_supplycost) as value
From partsupp, supplier, nation
Where s_suppkey = ps_suppkey and s_nationkey = n_nationkey and n_name  = 'ARGENTINA'
Group By ps_comment
Order By value desc, ps_comment asc
Limit 100;