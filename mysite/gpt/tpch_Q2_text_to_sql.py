import sys

from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI()

text_2_sql_prompt = """Give me SQL for the following text:

The query finds, in a given Rashtra, for each Vastuvivara of a 'BRASS' type and size 15, 
the Sarabharajudara who can supply it at minimum cost. 
If several Sarabharajudara in that Rashtra offer the desired 
Vastuvivara type and size at the same (minimum) cost, 
the query lists the Vastuvivara from Sarabharajudara with the 100 
highest account balances. For each Sarabharajudara, the query lists the 
Sarabharajudara's account balance, 
name, and Rashtra; 
the Vastuvivara's number and manufacturer; 
the Sarabharajudara's address, 
phone number and comment information.

Give only the SQL, do not add any explaination.
Put the SQL within python style comment quotes.

Consider the following schema while formulating the SQL query:

CREATE TABLE Rashtra (
    r_rashtrakramank INTEGER PRIMARY KEY,
    r_rashtranama VARCHAR(25),
    r_rashtramaahiti VARCHAR(152),
    r_pradeshakramank INTEGER
);

CREATE TABLE Pradesh (
    p_pradeshakramank INTEGER PRIMARY KEY,
    p_pradeshanama VARCHAR(25),
    p_pradeshamaahiti VARCHAR(152)
);

CREATE TABLE Graahaka (
    g_graahakakramank INTEGER PRIMARY KEY,
    g_graahakanama VARCHAR(25),
    g_graahakavyavahari VARCHAR(40),
    g_graahakathikana VARCHAR(40),
    g_graahakavishaya VARCHAR(15),
    g_graahakamaahiti VARCHAR(117),
    g_graahakakhata DOUBLE PRECISION,
    g_rashtrakramank INTEGER REFERENCES Rashtra(r_rashtrakramank)
);

CREATE TABLE Sarabharajudara (
    s_sarabharajudarakramank INTEGER PRIMARY KEY,
    s_sarabharajudaranama VARCHAR(25),
    s_sarabharajudaravyavahari VARCHAR(40),
    s_sarabharajudarathikana VARCHAR(40),
    s_sarabharajudaravishaya VARCHAR(15),
    s_sarabharajudaramaahiti VARCHAR(101),
    s_sarabharajudarakhata DOUBLE PRECISION,
    s_rashtrakramank INTEGER REFERENCES Rashtra(r_rashtrakramank)
);

CREATE TABLE Vastuvivara (
    v_vastukramank INTEGER PRIMARY KEY,
    v_vastunama VARCHAR(55),
    v_vastubranda VARCHAR(25),
    v_vastupaddhati VARCHAR(10),
    v_vastuvivara VARCHAR(23),
    v_vastukurita DOUBLE PRECISION,
    v_vastuyogyate VARCHAR(10),
    v_pradeshakramank INTEGER REFERENCES Pradesh(p_pradeshakramank)
);

CREATE TABLE Sarabharajudaravastu (
    sv_vastukramank INTEGER REFERENCES Vastuvivara(v_vastukramank),
    sv_sarabharajudarakramank INTEGER REFERENCES Sarabharajudara(s_sarabharajudarakramank),
    sv_vastubelav DOUBLE PRECISION,
    sv_vastukanishta INTEGER,
    sv_vastuvivara VARCHAR(199),
    PRIMARY KEY (sv_vastukramank, sv_sarabharajudarakramank)
);

CREATE TABLE Aajna (
    a_aajnakramank INTEGER PRIMARY KEY,
    a_graahakakramank INTEGER REFERENCES Graahaka(g_graahakakramank),
    a_aajnatharikh DATE,
    a_aajnathapradana DOUBLE PRECISION,
    a_aajnasthiti CHAR(1),
    a_aajnamahiti VARCHAR(79)
);

CREATE TABLE Aajnavastu (
    av_aajnakramank INTEGER REFERENCES Aajna(a_aajnakramank),
    av_vastukramank INTEGER REFERENCES Vastuvivara(v_vastukramank),
    av_sarabharajudarakramank INTEGER REFERENCES Sarabharajudara(s_sarabharajudarakramank),
    av_vastusankhya INTEGER,
    av_vastubela DOUBLE PRECISION,
    av_discount DOUBLE PRECISION,
    av_kar DOUBLE PRECISION,
    av_vastusanket CHAR(1),
    av_vastusamahita DATE,
    av_vastupoorakathe DATE,
    av_vastusamapti DATE,
    av_vastutharate CHAR(1),
    av_vastumahiti VARCHAR(44),
    PRIMARY KEY (av_aajnakramank, av_vastukramank, av_sarabharajudarakramank)
);

Mandatory instructions on query formulation:
1. Do not use redundant join conditions.
2. Do not use any predicate with place holder parameter.
3. No attribute in the database has NULL value.
4. Do not use predicate on any other attribute than that are used in the following query:

SELECT s_sarabharajudarakhata AS s_acctbal, 
       s_sarabharajudaranama AS s_name, 
       r_rashtranama AS n_name, 
       v_vastukramank AS p_partkey, 
       v_vastubranda AS p_mfgr, 
       s_sarabharajudarathikana AS s_address, 
       s_sarabharajudaravyavahari AS s_phone, 
       s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r, 
     Vastuvivara AS v, 
     Sarabharajudaravastu AS sv, 
     Sarabharajudara AS s, 
     Pradesh AS p
WHERE r.r_rashtrakramank = s.s_rashtrakramank
  AND v.v_pradeshakramank = p.p_pradeshakramank
  AND sv.sv_vastukramank = v.v_vastukramank
  AND sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
  AND v.v_vastupaddhati = '15'
  AND r.r_rashtranama = 'EUROPE'
  AND v.v_vastunama LIKE '%BRASS'; 

5. The attributes present in projections are accurate, use them in projection. 
6. Also use the projection aliases used in the query.
7. Use the tables present in the FROM clause of the query in your query. No table appears more than once in the query.
8. Order by of the above query is accurate, reuse it.
9. Text-based filter predicates of the above query are accurate, however they may be 
scattered around subqueries in the expected query.

Strictly follow the above instructions while formulating the query.

The output produced by the above query should be:
9938.53	"Sarabharajudara#000005359"	"UNITED KINGDOM           "	185358	"Manufacturer#4           "	"QKuHYh,vZGiwu2FWEJoLDx04"	"33-429-790-6131"	"uriously regular requests hag"
9938.53	"Sarabharajudara#000005359"	"UNITED KINGDOM           "	185358	"Manufacturer#4           "	"QKuHYh,vZGiwu2FWEJoLDx04"	"33-429-790-6131"	"uriously regular requests hag"
9937.84	"Sarabharajudara#000005969"	"ROMANIA                  "	108438	"Manufacturer#1           "	"ANDENSOSmk,miq23Xfb5RWt6dvUcvt6Qa"	"29-520-692-3537"	"efully express instructions. regular requests against the slyly fin"
9937.84	"Sarabharajudara#000005969"	"ROMANIA                  "	108438	"Manufacturer#1           "	"ANDENSOSmk,miq23Xfb5RWt6dvUcvt6Qa"	"29-520-692-3537"	"efully express instructions. regular requests against the slyly fin"
9936.22	"Sarabharajudara#000005250"	"UNITED KINGDOM           "	249	"Manufacturer#4           "	"B3rqp0xbSEim4Mpy2RH J"	"33-320-228-2957"	"etect about the furiously final accounts. slyly ironic pinto beans sleep inside the furiously"
9936.22	"Sarabharajudara#000005250"	"UNITED KINGDOM           "	249	"Manufacturer#4           "	"B3rqp0xbSEim4Mpy2RH J"	"33-320-228-2957"	"etect about the furiously final accounts. slyly ironic pinto beans sleep inside the furiously"
9923.77	"Sarabharajudara#000002324"	"GERMANY                  "	29821	"Manufacturer#4           "	"y3OD9UywSTOk"	"17-779-299-1839"	"ackages boost blithely. blithely regular deposits c"
9923.77	"Sarabharajudara#000002324"	"GERMANY                  "	29821	"Manufacturer#4           "	"y3OD9UywSTOk"	"17-779-299-1839"	"ackages boost blithely. blithely regular deposits c"
9871.22	"Sarabharajudara#000006373"	"GERMANY                  "	43868	"Manufacturer#5           "	"J8fcXWsTqM"	"17-813-485-8637"	"etect blithely bold asymptotes. fluffily ironic platelets wake furiously; blit"
9871.22	"Sarabharajudara#000006373"	"GERMANY                  "	43868	"Manufacturer#5           "	"J8fcXWsTqM"	"17-813-485-8637"	"etect blithely bold asymptotes. fluffily ironic platelets wake furiously; blit"
9870.78	"Sarabharajudara#000001286"	"GERMANY                  "	81285	"Manufacturer#2           "	"YKA,E2fjiVd7eUrzp2Ef8j1QxGo2DFnosaTEH"	"17-516-924-4574"	" regular accounts. furiously unusual courts above the fi"
9870.78	"Sarabharajudara#000001286"	"GERMANY                  "	81285	"Manufacturer#2           "	"YKA,E2fjiVd7eUrzp2Ef8j1QxGo2DFnosaTEH"	"17-516-924-4574"	" regular accounts. furiously unusual courts above the fi"
9870.78	"Sarabharajudara#000001286"	"GERMANY                  "	181285	"Manufacturer#4           "	"YKA,E2fjiVd7eUrzp2Ef8j1QxGo2DFnosaTEH"	"17-516-924-4574"	" regular accounts. furiously unusual courts above the fi"
9870.78	"Sarabharajudara#000001286"	"GERMANY                  "	181285	"Manufacturer#4           "	"YKA,E2fjiVd7eUrzp2Ef8j1QxGo2DFnosaTEH"	"17-516-924-4574"	" regular accounts. furiously unusual courts above the fi"
9852.52	"Sarabharajudara#000008973"	"RUSSIA                   "	18972	"Manufacturer#2           "	"t5L67YdBYYH6o,Vz24jpDyQ9"	"32-188-594-7038"	"rns wake final foxes. carefully unusual depende"
9852.52	"Sarabharajudara#000008973"	"RUSSIA                   "	18972	"Manufacturer#2           "	"t5L67YdBYYH6o,Vz24jpDyQ9"	"32-188-594-7038"	"rns wake final foxes. carefully unusual depende"
9847.83	"Sarabharajudara#000008097"	"RUSSIA                   "	130557	"Manufacturer#2           "	"xMe97bpE69NzdwLoX"	"32-375-640-3593"	" the special excuses. silent sentiments serve carefully final ac"
9847.83	"Sarabharajudara#000008097"	"RUSSIA                   "	130557	"Manufacturer#2           "	"xMe97bpE69NzdwLoX"	"32-375-640-3593"	" the special excuses. silent sentiments serve carefully final ac"
9847.57	"Sarabharajudara#000006345"	"FRANCE                   "	86344	"Manufacturer#1           "	"VSt3rzk3qG698u6ld8HhOByvrTcSTSvQlDQDag"	"16-886-766-7945"	"ges. slyly regular requests are. ruthless, express excuses cajole blithely across the unu"
9847.57	"Sarabharajudara#000006345"	"FRANCE                   "	86344	"Manufacturer#1           "	"VSt3rzk3qG698u6ld8HhOByvrTcSTSvQlDQDag"	"16-886-766-7945"	"ges. slyly regular requests are. ruthless, express excuses cajole blithely across the unu"
9847.57	"Sarabharajudara#000006345"	"FRANCE                   "	173827	"Manufacturer#2           "	"VSt3rzk3qG698u6ld8HhOByvrTcSTSvQlDQDag"	"16-886-766-7945"	"ges. slyly regular requests are. ruthless, express excuses cajole blithely across the unu"
9847.57	"Sarabharajudara#000006345"	"FRANCE                   "	173827	"Manufacturer#2           "	"VSt3rzk3qG698u6ld8HhOByvrTcSTSvQlDQDag"	"16-886-766-7945"	"ges. slyly regular requests are. ruthless, express excuses cajole blithely across the unu"
9836.93	"Sarabharajudara#000007342"	"RUSSIA                   "	4841	"Manufacturer#4           "	"JOlK7C1,7xrEZSSOw"	"32-399-414-5385"	"blithely carefully bold theodolites. fur"
9836.93	"Sarabharajudara#000007342"	"RUSSIA                   "	4841	"Manufacturer#4           "	"JOlK7C1,7xrEZSSOw"	"32-399-414-5385"	"blithely carefully bold theodolites. fur"
9817.10	"Sarabharajudara#000002352"	"RUSSIA                   "	124815	"Manufacturer#2           "	"4LfoHUZjgjEbAKw TgdKcgOc4D4uCYw"	"32-551-831-1437"	"wake carefully alongside of the carefully final ex"
9817.10	"Sarabharajudara#000002352"	"RUSSIA                   "	124815	"Manufacturer#2           "	"4LfoHUZjgjEbAKw TgdKcgOc4D4uCYw"	"32-551-831-1437"	"wake carefully alongside of the carefully final ex"
9817.10	"Sarabharajudara#000002352"	"RUSSIA                   "	152351	"Manufacturer#3           "	"4LfoHUZjgjEbAKw TgdKcgOc4D4uCYw"	"32-551-831-1437"	"wake carefully alongside of the carefully final ex"
9817.10	"Sarabharajudara#000002352"	"RUSSIA                   "	152351	"Manufacturer#3           "	"4LfoHUZjgjEbAKw TgdKcgOc4D4uCYw"	"32-551-831-1437"	"wake carefully alongside of the carefully final ex"
9739.86	"Sarabharajudara#000003384"	"FRANCE                   "	138357	"Manufacturer#2           "	"o,Z3v4POifevE k9U1b 6J1ucX,I"	"16-494-913-5925"	"s after the furiously bold packages sleep fluffily idly final requests: quickly final"
9739.86	"Sarabharajudara#000003384"	"FRANCE                   "	138357	"Manufacturer#2           "	"o,Z3v4POifevE k9U1b 6J1ucX,I"	"16-494-913-5925"	"s after the furiously bold packages sleep fluffily idly final requests: quickly final"
9721.95	"Sarabharajudara#000008757"	"UNITED KINGDOM           "	156241	"Manufacturer#3           "	"Atg6GnM4dT2"	"33-821-407-2995"	"eep furiously sauternes; quickl"
9721.95	"Sarabharajudara#000008757"	"UNITED KINGDOM           "	156241	"Manufacturer#3           "	"Atg6GnM4dT2"	"33-821-407-2995"	"eep furiously sauternes; quickl"
9681.33	"Sarabharajudara#000008406"	"RUSSIA                   "	78405	"Manufacturer#1           "	",qUuXcftUl"	"32-139-873-8571"	"haggle slyly regular excuses. quic"
9681.33	"Sarabharajudara#000008406"	"RUSSIA                   "	78405	"Manufacturer#1           "	",qUuXcftUl"	"32-139-873-8571"	"haggle slyly regular excuses. quic"
9643.55	"Sarabharajudara#000005148"	"ROMANIA                  "	107617	"Manufacturer#1           "	"kT4ciVFslx9z4s79p Js825"	"29-252-617-4850"	"final excuses. final ideas boost quickly furiously speci"
9643.55	"Sarabharajudara#000005148"	"ROMANIA                  "	107617	"Manufacturer#1           "	"kT4ciVFslx9z4s79p Js825"	"29-252-617-4850"	"final excuses. final ideas boost quickly furiously speci"
9624.82	"Sarabharajudara#000001816"	"FRANCE                   "	34306	"Manufacturer#3           "	"e7vab91vLJPWxxZnewmnDBpDmxYHrb"	"16-392-237-6726"	"e packages are around the special ideas. special, pending foxes us"
9624.82	"Sarabharajudara#000001816"	"FRANCE                   "	34306	"Manufacturer#3           "	"e7vab91vLJPWxxZnewmnDBpDmxYHrb"	"16-392-237-6726"	"e packages are around the special ideas. special, pending foxes us"
9624.78	"Sarabharajudara#000009658"	"ROMANIA                  "	189657	"Manufacturer#1           "	"oE9uBgEfSS4opIcepXyAYM,x"	"29-748-876-2014"	"ronic asymptotes wake bravely final"
9624.78	"Sarabharajudara#000009658"	"ROMANIA                  "	189657	"Manufacturer#1           "	"oE9uBgEfSS4opIcepXyAYM,x"	"29-748-876-2014"	"ronic asymptotes wake bravely final"
9612.94	"Sarabharajudara#000003228"	"ROMANIA                  "	120715	"Manufacturer#2           "	"KDdpNKN3cWu7ZSrbdqp7AfSLxx,qWB"	"29-325-784-8187"	"warhorses. quickly even deposits sublate daringly ironic instructions. slyly blithe t"
9612.94	"Sarabharajudara#000003228"	"ROMANIA                  "	120715	"Manufacturer#2           "	"KDdpNKN3cWu7ZSrbdqp7AfSLxx,qWB"	"29-325-784-8187"	"warhorses. quickly even deposits sublate daringly ironic instructions. slyly blithe t"
9612.94	"Sarabharajudara#000003228"	"ROMANIA                  "	198189	"Manufacturer#4           "	"KDdpNKN3cWu7ZSrbdqp7AfSLxx,qWB"	"29-325-784-8187"	"warhorses. quickly even deposits sublate daringly ironic instructions. slyly blithe t"
9612.94	"Sarabharajudara#000003228"	"ROMANIA                  "	198189	"Manufacturer#4           "	"KDdpNKN3cWu7ZSrbdqp7AfSLxx,qWB"	"29-325-784-8187"	"warhorses. quickly even deposits sublate daringly ironic instructions. slyly blithe t"
9571.83	"Sarabharajudara#000004305"	"ROMANIA                  "	179270	"Manufacturer#2           "	"qNHZ7WmCzygwMPRDO9Ps"	"29-973-481-1831"	"kly carefully express asymptotes. furiou"
9571.83	"Sarabharajudara#000004305"	"ROMANIA                  "	179270	"Manufacturer#2           "	"qNHZ7WmCzygwMPRDO9Ps"	"29-973-481-1831"	"kly carefully express asymptotes. furiou"
9558.10	"Sarabharajudara#000003532"	"UNITED KINGDOM           "	88515	"Manufacturer#4           "	"EOeuiiOn21OVpTlGguufFDFsbN1p0lhpxHp"	"33-152-301-2164"	" foxes. quickly even excuses use. slyly special foxes nag bl"
9558.10	"Sarabharajudara#000003532"	"UNITED KINGDOM           "	88515	"Manufacturer#4           "	"EOeuiiOn21OVpTlGguufFDFsbN1p0lhpxHp"	"33-152-301-2164"	" foxes. quickly even excuses use. slyly special foxes nag bl"
9492.79	"Sarabharajudara#000005975"	"GERMANY                  "	25974	"Manufacturer#5           "	"S6mIiCTx82z7lV"	"17-992-579-4839"	"arefully pending accounts. blithely regular excuses boost carefully carefully ironic p"
9492.79	"Sarabharajudara#000005975"	"GERMANY                  "	25974	"Manufacturer#5           "	"S6mIiCTx82z7lV"	"17-992-579-4839"	"arefully pending accounts. blithely regular excuses boost carefully carefully ironic p"
9461.05	"Sarabharajudara#000002536"	"UNITED KINGDOM           "	20033	"Manufacturer#1           "	"8mmGbyzaU 7ZS2wJumTibypncu9pNkDc4FYA"	"33-556-973-5522"	". slyly regular deposits wake slyly. furiously regular warthogs are."
9461.05	"Sarabharajudara#000002536"	"UNITED KINGDOM           "	20033	"Manufacturer#1           "	"8mmGbyzaU 7ZS2wJumTibypncu9pNkDc4FYA"	"33-556-973-5522"	". slyly regular deposits wake slyly. furiously regular warthogs are."
9453.01	"Sarabharajudara#000000802"	"ROMANIA                  "	175767	"Manufacturer#1           "	",6HYXb4uaHITmtMBj4Ak57Pd"	"29-342-882-6463"	"gular frets. permanently special multipliers believe blithely alongs"
9453.01	"Sarabharajudara#000000802"	"ROMANIA                  "	175767	"Manufacturer#1           "	",6HYXb4uaHITmtMBj4Ak57Pd"	"29-342-882-6463"	"gular frets. permanently special multipliers believe blithely alongs"
9408.65	"Sarabharajudara#000007772"	"UNITED KINGDOM           "	117771	"Manufacturer#4           "	"AiC5YAH,gdu0i7"	"33-152-491-1126"	"nag against the final requests. furiously unusual packages cajole blit"
9408.65	"Sarabharajudara#000007772"	"UNITED KINGDOM           "	117771	"Manufacturer#4           "	"AiC5YAH,gdu0i7"	"33-152-491-1126"	"nag against the final requests. furiously unusual packages cajole blit"
9359.61	"Sarabharajudara#000004856"	"ROMANIA                  "	62349	"Manufacturer#5           "	"HYogcF3Jb yh1"	"29-334-870-9731"	"y ironic theodolites. blithely sile"
9359.61	"Sarabharajudara#000004856"	"ROMANIA                  "	62349	"Manufacturer#5           "	"HYogcF3Jb yh1"	"29-334-870-9731"	"y ironic theodolites. blithely sile"
9357.45	"Sarabharajudara#000006188"	"UNITED KINGDOM           "	138648	"Manufacturer#1           "	"g801,ssP8wpTk4Hm"	"33-583-607-1633"	"ously always regular packages. fluffily even accounts beneath the furiously final pack"
9357.45	"Sarabharajudara#000006188"	"UNITED KINGDOM           "	138648	"Manufacturer#1           "	"g801,ssP8wpTk4Hm"	"33-583-607-1633"	"ously always regular packages. fluffily even accounts beneath the furiously final pack"
9352.04	"Sarabharajudara#000003439"	"GERMANY                  "	170921	"Manufacturer#4           "	"qYPDgoiBGhCYxjgC"	"17-128-996-4650"	" according to the carefully bold ideas"
9352.04	"Sarabharajudara#000003439"	"GERMANY                  "	170921	"Manufacturer#4           "	"qYPDgoiBGhCYxjgC"	"17-128-996-4650"	" according to the carefully bold ideas"
9312.97	"Sarabharajudara#000007807"	"RUSSIA                   "	90279	"Manufacturer#5           "	"oGYMPCk9XHGB2PBfKRnHA"	"32-673-872-5854"	"ecial packages among the pending, even requests use regula"
9312.97	"Sarabharajudara#000007807"	"RUSSIA                   "	90279	"Manufacturer#5           "	"oGYMPCk9XHGB2PBfKRnHA"	"32-673-872-5854"	"ecial packages among the pending, even requests use regula"
9312.97	"Sarabharajudara#000007807"	"RUSSIA                   "	100276	"Manufacturer#5           "	"oGYMPCk9XHGB2PBfKRnHA"	"32-673-872-5854"	"ecial packages among the pending, even requests use regula"
9312.97	"Sarabharajudara#000007807"	"RUSSIA                   "	100276	"Manufacturer#5           "	"oGYMPCk9XHGB2PBfKRnHA"	"32-673-872-5854"	"ecial packages among the pending, even requests use regula"
9280.27	"Sarabharajudara#000007194"	"ROMANIA                  "	47193	"Manufacturer#3           "	"zhRUQkBSrFYxIAXTfInj vyGRQjeK"	"29-318-454-2133"	"o beans haggle after the furiously unusual deposits. carefully silent dolphins cajole carefully"
9280.27	"Sarabharajudara#000007194"	"ROMANIA                  "	47193	"Manufacturer#3           "	"zhRUQkBSrFYxIAXTfInj vyGRQjeK"	"29-318-454-2133"	"o beans haggle after the furiously unusual deposits. carefully silent dolphins cajole carefully"
9274.80	"Sarabharajudara#000008854"	"RUSSIA                   "	76346	"Manufacturer#3           "	"1xhLoOUM7I3mZ1mKnerw OSqdbb4QbGa"	"32-524-148-5221"	"y. courts do wake slyly. carefully ironic platelets haggle above the slyly regular the"
9274.80	"Sarabharajudara#000008854"	"RUSSIA                   "	76346	"Manufacturer#3           "	"1xhLoOUM7I3mZ1mKnerw OSqdbb4QbGa"	"32-524-148-5221"	"y. courts do wake slyly. carefully ironic platelets haggle above the slyly regular the"
9249.35	"Sarabharajudara#000003973"	"FRANCE                   "	26466	"Manufacturer#1           "	"d18GiDsL6Wm2IsGXM,RZf1jCsgZAOjNYVThTRP4"	"16-722-866-1658"	"uests are furiously. regular tithes through the regular, final accounts cajole furiously above the q"
9249.35	"Sarabharajudara#000003973"	"FRANCE                   "	26466	"Manufacturer#1           "	"d18GiDsL6Wm2IsGXM,RZf1jCsgZAOjNYVThTRP4"	"16-722-866-1658"	"uests are furiously. regular tithes through the regular, final accounts cajole furiously above the q"
9249.35	"Sarabharajudara#000003973"	"FRANCE                   "	33972	"Manufacturer#1           "	"d18GiDsL6Wm2IsGXM,RZf1jCsgZAOjNYVThTRP4"	"16-722-866-1658"	"uests are furiously. regular tithes through the regular, final accounts cajole furiously above the q"
9249.35	"Sarabharajudara#000003973"	"FRANCE                   "	33972	"Manufacturer#1           "	"d18GiDsL6Wm2IsGXM,RZf1jCsgZAOjNYVThTRP4"	"16-722-866-1658"	"uests are furiously. regular tithes through the regular, final accounts cajole furiously above the q"
9208.70	"Sarabharajudara#000007769"	"ROMANIA                  "	40256	"Manufacturer#5           "	"rsimdze 5o9P Ht7xS"	"29-964-424-9649"	"lites was quickly above the furiously ironic requests. slyly even foxes against the blithely bold "
9208.70	"Sarabharajudara#000007769"	"ROMANIA                  "	40256	"Manufacturer#5           "	"rsimdze 5o9P Ht7xS"	"29-964-424-9649"	"lites was quickly above the furiously ironic requests. slyly even foxes against the blithely bold "
9201.47	"Sarabharajudara#000009690"	"UNITED KINGDOM           "	67183	"Manufacturer#5           "	"CB BnUTlmi5zdeEl7R7"	"33-121-267-9529"	"e even, even foxes. blithely ironic packages cajole regular packages. slyly final ide"
9201.47	"Sarabharajudara#000009690"	"UNITED KINGDOM           "	67183	"Manufacturer#5           "	"CB BnUTlmi5zdeEl7R7"	"33-121-267-9529"	"e even, even foxes. blithely ironic packages cajole regular packages. slyly final ide"
9192.10	"Sarabharajudara#000000115"	"UNITED KINGDOM           "	85098	"Manufacturer#3           "	"nJ 2t0f7Ve,wL1,6WzGBJLNBUCKlsV"	"33-597-248-1220"	"es across the carefully express accounts boost caref"
9192.10	"Sarabharajudara#000000115"	"UNITED KINGDOM           "	85098	"Manufacturer#3           "	"nJ 2t0f7Ve,wL1,6WzGBJLNBUCKlsV"	"33-597-248-1220"	"es across the carefully express accounts boost caref"
9189.98	"Sarabharajudara#000001226"	"GERMANY                  "	21225	"Manufacturer#4           "	"qsLCqSvLyZfuXIpjz"	"17-725-903-1381"	" deposits. blithely bold excuses about the slyly bold forges wake "
9189.98	"Sarabharajudara#000001226"	"GERMANY                  "	21225	"Manufacturer#4           "	"qsLCqSvLyZfuXIpjz"	"17-725-903-1381"	" deposits. blithely bold excuses about the slyly bold forges wake "
9128.97	"Sarabharajudara#000004311"	"RUSSIA                   "	146768	"Manufacturer#5           "	"I8IjnXd7NSJRs594RxsRR0"	"32-155-440-7120"	"refully. blithely unusual asymptotes haggle "
9128.97	"Sarabharajudara#000004311"	"RUSSIA                   "	146768	"Manufacturer#5           "	"I8IjnXd7NSJRs594RxsRR0"	"32-155-440-7120"	"refully. blithely unusual asymptotes haggle "
9104.83	"Sarabharajudara#000008520"	"GERMANY                  "	150974	"Manufacturer#4           "	"RqRVDgD0ER J9 b41vR2,3"	"17-728-804-1793"	"ly about the blithely ironic depths. slyly final theodolites among the fluffily bold ideas print"
9104.83	"Sarabharajudara#000008520"	"GERMANY                  "	150974	"Manufacturer#4           "	"RqRVDgD0ER J9 b41vR2,3"	"17-728-804-1793"	"ly about the blithely ironic depths. slyly final theodolites among the fluffily bold ideas print"
9101.00	"Sarabharajudara#000005791"	"ROMANIA                  "	128254	"Manufacturer#5           "	"zub2zCV,jhHPPQqi,P2INAjE1zI n66cOEoXFG"	"29-549-251-5384"	"ts. notornis detect blithely above the carefully bold requests. blithely even package"
9101.00	"Sarabharajudara#000005791"	"ROMANIA                  "	128254	"Manufacturer#5           "	"zub2zCV,jhHPPQqi,P2INAjE1zI n66cOEoXFG"	"29-549-251-5384"	"ts. notornis detect blithely above the carefully bold requests. blithely even package"
9094.57	"Sarabharajudara#000004582"	"RUSSIA                   "	39575	"Manufacturer#1           "	"WB0XkCSG3r,mnQ n,h9VIxjjr9ARHFvKgMDf"	"32-587-577-1351"	"jole. regular accounts sleep blithely frets. final pinto beans play furiously past the "
9094.57	"Sarabharajudara#000004582"	"RUSSIA                   "	39575	"Manufacturer#1           "	"WB0XkCSG3r,mnQ n,h9VIxjjr9ARHFvKgMDf"	"32-587-577-1351"	"jole. regular accounts sleep blithely frets. final pinto beans play furiously past the "
8996.87	"Sarabharajudara#000004702"	"FRANCE                   "	102191	"Manufacturer#5           "	"8XVcQK23akp"	"16-811-269-8946"	"ickly final packages along the express plat"
8996.87	"Sarabharajudara#000004702"	"FRANCE                   "	102191	"Manufacturer#5           "	"8XVcQK23akp"	"16-811-269-8946"	"ickly final packages along the express plat"
8996.14	"Sarabharajudara#000009814"	"ROMANIA                  "	139813	"Manufacturer#2           "	"af0O5pg83lPU4IDVmEylXZVqYZQzSDlYLAmR"	"29-995-571-8781"	" dependencies boost quickly across the furiously pending requests! unusual dolphins play sl"
8996.14	"Sarabharajudara#000009814"	"ROMANIA                  "	139813	"Manufacturer#2           "	"af0O5pg83lPU4IDVmEylXZVqYZQzSDlYLAmR"	"29-995-571-8781"	" dependencies boost quickly across the furiously pending requests! unusual dolphins play sl"
8968.42	"Sarabharajudara#000010000"	"ROMANIA                  "	119999	"Manufacturer#5           "	"aTGLEusCiL4F PDBdv665XBJhPyCOB0i"	"29-578-432-2146"	"ly regular foxes boost slyly. quickly special waters boost carefully ironi"
8968.42	"Sarabharajudara#000010000"	"ROMANIA                  "	119999	"Manufacturer#5           "	"aTGLEusCiL4F PDBdv665XBJhPyCOB0i"	"29-578-432-2146"	"ly regular foxes boost slyly. quickly special waters boost carefully ironi"
8936.82	"Sarabharajudara#000007043"	"UNITED KINGDOM           "	109512	"Manufacturer#1           "	"FVajceZInZdbJE6Z9XsRUxrUEpiwHDrOXi,1Rz"	"33-784-177-8208"	"efully regular courts. furiousl"
8936.82	"Sarabharajudara#000007043"	"UNITED KINGDOM           "	109512	"Manufacturer#1           "	"FVajceZInZdbJE6Z9XsRUxrUEpiwHDrOXi,1Rz"	"33-784-177-8208"	"efully regular courts. furiousl"
8929.42	"Sarabharajudara#000008770"	"FRANCE                   "	173735	"Manufacturer#4           "	"R7cG26TtXrHAP9 HckhfRi"	"16-242-746-9248"	"cajole furiously unusual requests. quickly stealthy requests are. "
8929.42	"Sarabharajudara#000008770"	"FRANCE                   "	173735	"Manufacturer#4           "	"R7cG26TtXrHAP9 HckhfRi"	"16-242-746-9248"	"cajole furiously unusual requests. quickly stealthy requests are. "
8920.59	"Sarabharajudara#000003967"	"ROMANIA                  "	26460	"Manufacturer#1           "	"eHoAXe62SY9"	"29-194-731-3944"	"aters. express, pending instructions sleep. brave, r"
8920.59	"Sarabharajudara#000003967"	"ROMANIA                  "	26460	"Manufacturer#1           "	"eHoAXe62SY9"	"29-194-731-3944"	"aters. express, pending instructions sleep. brave, r"
8920.59	"Sarabharajudara#000003967"	"ROMANIA                  "	173966	"Manufacturer#2           "	"eHoAXe62SY9"	"29-194-731-3944"	"aters. express, pending instructions sleep. brave, r"
8920.59	"Sarabharajudara#000003967"	"ROMANIA                  "	173966	"Manufacturer#2           "	"eHoAXe62SY9"	"29-194-731-3944"	"aters. express, pending instructions sleep. brave, r"
8913.96	"Sarabharajudara#000004603"	"UNITED KINGDOM           "	137063	"Manufacturer#2           "	"OUzlvMUr7n,utLxmPNeYKSf3T24OXskxB5"	"33-789-255-7342"	" haggle slyly above the furiously regular pinto beans. even "
8913.96	"Sarabharajudara#000004603"	"UNITED KINGDOM           "	137063	"Manufacturer#2           "	"OUzlvMUr7n,utLxmPNeYKSf3T24OXskxB5"	"33-789-255-7342"	" haggle slyly above the furiously regular pinto beans. even "
8877.82	"Sarabharajudara#000007967"	"FRANCE                   "	167966	"Manufacturer#5           "	"A3pi1BARM4nx6R,qrwFoRPU"	"16-442-147-9345"	"ously foxes. express, ironic requests im"
8877.82	"Sarabharajudara#000007967"	"FRANCE                   "	167966	"Manufacturer#5           "	"A3pi1BARM4nx6R,qrwFoRPU"	"16-442-147-9345"	"ously foxes. express, ironic requests im"
8862.24	"Sarabharajudara#000003323"	"ROMANIA                  "	73322	"Manufacturer#3           "	"W9 lYcsC9FwBqk3ItL"	"29-736-951-3710"	"ly pending ideas sleep about the furiously unu"
8862.24	"Sarabharajudara#000003323"	"ROMANIA                  "	73322	"Manufacturer#3           "	"W9 lYcsC9FwBqk3ItL"	"29-736-951-3710"	"ly pending ideas sleep about the furiously unu"
8841.59	"Sarabharajudara#000005750"	"ROMANIA                  "	100729	"Manufacturer#5           "	"Erx3lAgu0g62iaHF9x50uMH4EgeN9hEG"	"29-344-502-5481"	"gainst the pinto beans. fluffily unusual dependencies affix slyly even deposits."
8841.59	"Sarabharajudara#000005750"	"ROMANIA                  "	100729	"Manufacturer#5           "	"Erx3lAgu0g62iaHF9x50uMH4EgeN9hEG"	"29-344-502-5481"	"gainst the pinto beans. fluffily unusual dependencies affix slyly even deposits."
8781.71	"Sarabharajudara#000003121"	"ROMANIA                  "	13120	"Manufacturer#5           "	"wNqTogx238ZYCamFb,50v,bj 4IbNFW9Bvw1xP"	"29-707-291-5144"	"s wake quickly ironic ideas"
8781.71	"Sarabharajudara#000003121"	"ROMANIA                  "	13120	"Manufacturer#5           "	"wNqTogx238ZYCamFb,50v,bj 4IbNFW9Bvw1xP"	"29-707-291-5144"	"s wake quickly ironic ideas"
8754.24	"Sarabharajudara#000009407"	"UNITED KINGDOM           "	179406	"Manufacturer#4           "	"CHRCbkaWcf5B"	"33-903-970-9604"	"e ironic requests. carefully even foxes above the furious"
8754.24	"Sarabharajudara#000009407"	"UNITED KINGDOM           "	179406	"Manufacturer#4           "	"CHRCbkaWcf5B"	"33-903-970-9604"	"e ironic requests. carefully even foxes above the furious"
8691.06	"Sarabharajudara#000004429"	"UNITED KINGDOM           "	126892	"Manufacturer#2           "	"k,BQms5UhoAF1B2Asi,fLib"	"33-964-337-5038"	"efully express deposits kindle after the deposits. final "
8691.06	"Sarabharajudara#000004429"	"UNITED KINGDOM           "	126892	"Manufacturer#2           "	"k,BQms5UhoAF1B2Asi,fLib"	"33-964-337-5038"	"efully express deposits kindle after the deposits. final "
8655.99	"Sarabharajudara#000006330"	"RUSSIA                   "	193810	"Manufacturer#2           "	"UozlaENr0ytKe2w6CeIEWFWn iO3S8Rae7Ou"	"32-561-198-3705"	"symptotes use about the express dolphins. requests use after the express platelets. final, ex"
8655.99	"Sarabharajudara#000006330"	"RUSSIA                   "	193810	"Manufacturer#2           "	"UozlaENr0ytKe2w6CeIEWFWn iO3S8Rae7Ou"	"32-561-198-3705"	"symptotes use about the express dolphins. requests use after the express platelets. final, ex"
8638.36	"Sarabharajudara#000002920"	"RUSSIA                   "	75398	"Manufacturer#1           "	"Je2a8bszf3L"	"32-122-621-7549"	"ly quickly ironic requests. even requests whithout t"
8638.36	"Sarabharajudara#000002920"	"RUSSIA                   "	75398	"Manufacturer#1           "	"Je2a8bszf3L"	"32-122-621-7549"	"ly quickly ironic requests. even requests whithout t"
8638.36	"Sarabharajudara#000002920"	"RUSSIA                   "	170402	"Manufacturer#3           "	"Je2a8bszf3L"	"32-122-621-7549"	"ly quickly ironic requests. even requests whithout t"
8638.36	"Sarabharajudara#000002920"	"RUSSIA                   "	170402	"Manufacturer#3           "	"Je2a8bszf3L"	"32-122-621-7549"	"ly quickly ironic requests. even requests whithout t"
8607.69	"Sarabharajudara#000006003"	"UNITED KINGDOM           "	76002	"Manufacturer#2           "	"EH9wADcEiuenM0NR08zDwMidw,52Y2RyILEiA"	"33-416-807-5206"	"ar, pending accounts. pending depende"
8607.69	"Sarabharajudara#000006003"	"UNITED KINGDOM           "	76002	"Manufacturer#2           "	"EH9wADcEiuenM0NR08zDwMidw,52Y2RyILEiA"	"33-416-807-5206"	"ar, pending accounts. pending depende"
8569.52	"Sarabharajudara#000005936"	"RUSSIA                   "	5935	"Manufacturer#5           "	"jXaNZ6vwnEWJ2ksLZJpjtgt0bY2a3AU"	"32-644-251-7916"	". regular foxes nag carefully atop the regular, silent deposits. quickly regular packages "
8569.52	"Sarabharajudara#000005936"	"RUSSIA                   "	5935	"Manufacturer#5           "	"jXaNZ6vwnEWJ2ksLZJpjtgt0bY2a3AU"	"32-644-251-7916"	". regular foxes nag carefully atop the regular, silent deposits. quickly regular packages "
8564.12	"Sarabharajudara#000000033"	"GERMANY                  "	110032	"Manufacturer#1           "	"gfeKpYw3400L0SDywXA6Ya1Qmq1w6YB9f3R"	"17-138-897-9374"	"n sauternes along the regular asymptotes are regularly along the "
8564.12	"Sarabharajudara#000000033"	"GERMANY                  "	110032	"Manufacturer#1           "	"gfeKpYw3400L0SDywXA6Ya1Qmq1w6YB9f3R"	"17-138-897-9374"	"n sauternes along the regular asymptotes are regularly along the "
8553.82	"Sarabharajudara#000003979"	"ROMANIA                  "	143978	"Manufacturer#4           "	"BfmVhCAnCMY3jzpjUMy4CNWs9 HzpdQR7INJU"	"29-124-646-4897"	"ic requests wake against the blithely unusual accounts. fluffily r"
8553.82	"Sarabharajudara#000003979"	"ROMANIA                  "	143978	"Manufacturer#4           "	"BfmVhCAnCMY3jzpjUMy4CNWs9 HzpdQR7INJU"	"29-124-646-4897"	"ic requests wake against the blithely unusual accounts. fluffily r"
8517.23	"Sarabharajudara#000009529"	"RUSSIA                   "	37025	"Manufacturer#5           "	"e44R8o7JAIS9iMcr"	"32-565-297-8775"	"ove the even courts. furiously special platelets "
8517.23	"Sarabharajudara#000009529"	"RUSSIA                   "	37025	"Manufacturer#5           "	"e44R8o7JAIS9iMcr"	"32-565-297-8775"	"ove the even courts. furiously special platelets "
8517.23	"Sarabharajudara#000009529"	"RUSSIA                   "	59528	"Manufacturer#2           "	"e44R8o7JAIS9iMcr"	"32-565-297-8775"	"ove the even courts. furiously special platelets "
8517.23	"Sarabharajudara#000009529"	"RUSSIA                   "	59528	"Manufacturer#2           "	"e44R8o7JAIS9iMcr"	"32-565-297-8775"	"ove the even courts. furiously special platelets "
8503.70	"Sarabharajudara#000006830"	"RUSSIA                   "	44325	"Manufacturer#4           "	"BC4WFCYRUZyaIgchU 4S"	"32-147-878-5069"	"pades cajole. furious packages among the carefully express excuses boost furiously across th"
8503.70	"Sarabharajudara#000006830"	"RUSSIA                   "	44325	"Manufacturer#4           "	"BC4WFCYRUZyaIgchU 4S"	"32-147-878-5069"	"pades cajole. furious packages among the carefully express excuses boost furiously across th"
8457.09	"Sarabharajudara#000009456"	"UNITED KINGDOM           "	19455	"Manufacturer#1           "	"7SBhZs8gP1cJjT0Qf433YBk"	"33-858-440-4349"	"cing requests along the furiously unusual deposits promise among the furiously unus"
8457.09	"Sarabharajudara#000009456"	"UNITED KINGDOM           "	19455	"Manufacturer#1           "	"7SBhZs8gP1cJjT0Qf433YBk"	"33-858-440-4349"	"cing requests along the furiously unusual deposits promise among the furiously unus"
8441.40	"Sarabharajudara#000003817"	"FRANCE                   "	141302	"Manufacturer#2           "	"hU3fz3xL78"	"16-339-356-5115"	"ely even ideas. ideas wake slyly furiously unusual instructions. pinto beans sleep ag"
8441.40	"Sarabharajudara#000003817"	"FRANCE                   "	141302	"Manufacturer#2           "	"hU3fz3xL78"	"16-339-356-5115"	"ely even ideas. ideas wake slyly furiously unusual instructions. pinto beans sleep ag"
8432.89	"Sarabharajudara#000003990"	"RUSSIA                   "	191470	"Manufacturer#1           "	"wehBBp1RQbfxAYDASS75MsywmsKHRVdkrvNe6m"	"32-839-509-9301"	"ep furiously. packages should have to haggle slyly across the deposits. furiously regu"
8432.89	"Sarabharajudara#000003990"	"RUSSIA                   "	191470	"Manufacturer#1           "	"wehBBp1RQbfxAYDASS75MsywmsKHRVdkrvNe6m"	"32-839-509-9301"	"ep furiously. packages should have to haggle slyly across the deposits. furiously regu"
8431.40	"Sarabharajudara#000002675"	"ROMANIA                  "	5174	"Manufacturer#1           "	"HJFStOu9R5NGPOegKhgbzBdyvrG2yh8w"	"29-474-643-1443"	"ithely express pinto beans. blithely even foxes haggle. furiously regular theodol"
8431.40	"Sarabharajudara#000002675"	"ROMANIA                  "	5174	"Manufacturer#1           "	"HJFStOu9R5NGPOegKhgbzBdyvrG2yh8w"	"29-474-643-1443"	"ithely express pinto beans. blithely even foxes haggle. furiously regular theodol"
8407.04	"Sarabharajudara#000005406"	"RUSSIA                   "	162889	"Manufacturer#4           "	"j7 gYF5RW8DC5UrjKC"	"32-626-152-4621"	"r the blithely regular packages. slyly ironic theodoli"
8407.04	"Sarabharajudara#000005406"	"RUSSIA                   "	162889	"Manufacturer#4           "	"j7 gYF5RW8DC5UrjKC"	"32-626-152-4621"	"r the blithely regular packages. slyly ironic theodoli"
8386.08	"Sarabharajudara#000008518"	"FRANCE                   "	36014	"Manufacturer#3           "	"2jqzqqAVe9crMVGP,n9nTsQXulNLTUYoJjEDcqWV"	"16-618-780-7481"	"blithely bold pains are carefully platelets. finally regular pinto beans sleep carefully special"
8386.08	"Sarabharajudara#000008518"	"FRANCE                   "	36014	"Manufacturer#3           "	"2jqzqqAVe9crMVGP,n9nTsQXulNLTUYoJjEDcqWV"	"16-618-780-7481"	"blithely bold pains are carefully platelets. finally regular pinto beans sleep carefully special"
8376.52	"Sarabharajudara#000005306"	"UNITED KINGDOM           "	190267	"Manufacturer#5           "	"9t8Y8 QqSIsoADPt6NLdk,TP5zyRx41oBUlgoGc9"	"33-632-514-7931"	"ly final accounts sleep special, regular requests. furiously regular"
8376.52	"Sarabharajudara#000005306"	"UNITED KINGDOM           "	190267	"Manufacturer#5           "	"9t8Y8 QqSIsoADPt6NLdk,TP5zyRx41oBUlgoGc9"	"33-632-514-7931"	"ly final accounts sleep special, regular requests. furiously regular"
8348.74	"Sarabharajudara#000008851"	"FRANCE                   "	66344	"Manufacturer#4           "	"nWxi7GwEbjhw1"	"16-796-240-2472"	" boldly final deposits. regular, even instructions detect slyly. fluffily unusual pinto bea"
8348.74	"Sarabharajudara#000008851"	"FRANCE                   "	66344	"Manufacturer#4           "	"nWxi7GwEbjhw1"	"16-796-240-2472"	" boldly final deposits. regular, even instructions detect slyly. fluffily unusual pinto bea"
8338.58	"Sarabharajudara#000007269"	"FRANCE                   "	17268	"Manufacturer#4           "	"ZwhJSwABUoiB04,3"	"16-267-277-4365"	"iously final accounts. even pinto beans cajole slyly regular"
8338.58	"Sarabharajudara#000007269"	"FRANCE                   "	17268	"Manufacturer#4           "	"ZwhJSwABUoiB04,3"	"16-267-277-4365"	"iously final accounts. even pinto beans cajole slyly regular"
8328.46	"Sarabharajudara#000001744"	"ROMANIA                  "	69237	"Manufacturer#5           "	"oLo3fV64q2,FKHa3p,qHnS7Yzv,ps8"	"29-330-728-5873"	"ep carefully-- even, careful packages are slyly along t"
8328.46	"Sarabharajudara#000001744"	"ROMANIA                  "	69237	"Manufacturer#5           "	"oLo3fV64q2,FKHa3p,qHnS7Yzv,ps8"	"29-330-728-5873"	"ep carefully-- even, careful packages are slyly along t"
8307.93	"Sarabharajudara#000003142"	"GERMANY                  "	18139	"Manufacturer#1           "	"dqblvV8dCNAorGlJ"	"17-595-447-6026"	"olites wake furiously regular decoys. final requests nod "
8307.93	"Sarabharajudara#000003142"	"GERMANY                  "	18139	"Manufacturer#1           "	"dqblvV8dCNAorGlJ"	"17-595-447-6026"	"olites wake furiously regular decoys. final requests nod "
8231.61	"Sarabharajudara#000009558"	"RUSSIA                   "	192000	"Manufacturer#2           "	"mcdgen,yT1iJDHDS5fV"	"32-762-137-5858"	" foxes according to the furi"
8231.61	"Sarabharajudara#000009558"	"RUSSIA                   "	192000	"Manufacturer#2           "	"mcdgen,yT1iJDHDS5fV"	"32-762-137-5858"	" foxes according to the furi"
8152.61	"Sarabharajudara#000002731"	"ROMANIA                  "	15227	"Manufacturer#4           "	" nluXJCuY1tu"	"29-805-463-2030"	" special requests. even, regular warhorses affix among the final gr"
8152.61	"Sarabharajudara#000002731"	"ROMANIA                  "	15227	"Manufacturer#4           "	" nluXJCuY1tu"	"29-805-463-2030"	" special requests. even, regular warhorses affix among the final gr"
8109.09	"Sarabharajudara#000009186"	"FRANCE                   "	99185	"Manufacturer#1           "	"wgfosrVPexl9pEXWywaqlBMDYYf"	"16-668-570-1402"	"tions haggle slyly about the sil"
8109.09	"Sarabharajudara#000009186"	"FRANCE                   "	99185	"Manufacturer#1           "	"wgfosrVPexl9pEXWywaqlBMDYYf"	"16-668-570-1402"	"tions haggle slyly about the sil"
8102.62	"Sarabharajudara#000003347"	"UNITED KINGDOM           "	18344	"Manufacturer#5           "	"m CtXS2S16i"	"33-454-274-8532"	"egrate with the slyly bold instructions. special foxes haggle silently among the"
8102.62	"Sarabharajudara#000003347"	"UNITED KINGDOM           "	18344	"Manufacturer#5           "	"m CtXS2S16i"	"33-454-274-8532"	"egrate with the slyly bold instructions. special foxes haggle silently among the"
8046.07	"Sarabharajudara#000008780"	"FRANCE                   "	191222	"Manufacturer#3           "	"AczzuE0UK9osj ,Lx0Jmh"	"16-473-215-6395"	"onic platelets cajole after the regular instructions. permanently bold excuses"
8046.07	"Sarabharajudara#000008780"	"FRANCE                   "	191222	"Manufacturer#3           "	"AczzuE0UK9osj ,Lx0Jmh"	"16-473-215-6395"	"onic platelets cajole after the regular instructions. permanently bold excuses"
8042.09	"Sarabharajudara#000003245"	"RUSSIA                   "	135705	"Manufacturer#4           "	"Dh8Ikg39onrbOL4DyTfGw8a9oKUX3d9Y"	"32-836-132-8872"	"osits. packages cajole slyly. furiously regular deposits cajole slyly. q"
8042.09	"Sarabharajudara#000003245"	"RUSSIA                   "	135705	"Manufacturer#4           "	"Dh8Ikg39onrbOL4DyTfGw8a9oKUX3d9Y"	"32-836-132-8872"	"osits. packages cajole slyly. furiously regular deposits cajole slyly. q"
8042.09	"Sarabharajudara#000003245"	"RUSSIA                   "	150729	"Manufacturer#1           "	"Dh8Ikg39onrbOL4DyTfGw8a9oKUX3d9Y"	"32-836-132-8872"	"osits. packages cajole slyly. furiously regular deposits cajole slyly. q"
8042.09	"Sarabharajudara#000003245"	"RUSSIA                   "	150729	"Manufacturer#1           "	"Dh8Ikg39onrbOL4DyTfGw8a9oKUX3d9Y"	"32-836-132-8872"	"osits. packages cajole slyly. furiously regular deposits cajole slyly. q"
7992.40	"Sarabharajudara#000006108"	"FRANCE                   "	118574	"Manufacturer#1           "	"8tBydnTDwUqfBfFV4l3"	"16-974-998-8937"	" ironic ideas? fluffily even instructions wake. blithel"
7992.40	"Sarabharajudara#000006108"	"FRANCE                   "	118574	"Manufacturer#1           "	"8tBydnTDwUqfBfFV4l3"	"16-974-998-8937"	" ironic ideas? fluffily even instructions wake. blithel"
7980.65	"Sarabharajudara#000001288"	"FRANCE                   "	13784	"Manufacturer#4           "	"zE,7HgVPrCn"	"16-646-464-8247"	"ully bold courts. escapades nag slyly. furiously fluffy theodo"
7980.65	"Sarabharajudara#000001288"	"FRANCE                   "	13784	"Manufacturer#4           "	"zE,7HgVPrCn"	"16-646-464-8247"	"ully bold courts. escapades nag slyly. furiously fluffy theodo"
7950.37	"Sarabharajudara#000008101"	"GERMANY                  "	33094	"Manufacturer#5           "	"kkYvL6IuvojJgTNG IKkaXQDYgx8ILohj"	"17-627-663-8014"	"arefully unusual requests x-ray above the quickly final deposits. "
7950.37	"Sarabharajudara#000008101"	"GERMANY                  "	33094	"Manufacturer#5           "	"kkYvL6IuvojJgTNG IKkaXQDYgx8ILohj"	"17-627-663-8014"	"arefully unusual requests x-ray above the quickly final deposits. "
7937.93	"Sarabharajudara#000009012"	"ROMANIA                  "	83995	"Manufacturer#2           "	"iUiTziH,Ek3i4lwSgunXMgrcTzwdb"	"29-250-925-9690"	"to the blithely ironic deposits nag sly"
7937.93	"Sarabharajudara#000009012"	"ROMANIA                  "	83995	"Manufacturer#2           "	"iUiTziH,Ek3i4lwSgunXMgrcTzwdb"	"29-250-925-9690"	"to the blithely ironic deposits nag sly"
7914.45	"Sarabharajudara#000001013"	"RUSSIA                   "	125988	"Manufacturer#2           "	"riRcntps4KEDtYScjpMIWeYF6mNnR"	"32-194-698-3365"	" busily bold packages are dolphi"
7914.45	"Sarabharajudara#000001013"	"RUSSIA                   "	125988	"Manufacturer#2           "	"riRcntps4KEDtYScjpMIWeYF6mNnR"	"32-194-698-3365"	" busily bold packages are dolphi"
7912.91	"Sarabharajudara#000004211"	"GERMANY                  "	159180	"Manufacturer#5           "	"2wQRVovHrm3,v03IKzfTd,1PYsFXQFFOG"	"17-266-947-7315"	"ay furiously regular platelets. cou"
7912.91	"Sarabharajudara#000004211"	"GERMANY                  "	159180	"Manufacturer#5           "	"2wQRVovHrm3,v03IKzfTd,1PYsFXQFFOG"	"17-266-947-7315"	"ay furiously regular platelets. cou"
7912.91	"Sarabharajudara#000004211"	"GERMANY                  "	184210	"Manufacturer#4           "	"2wQRVovHrm3,v03IKzfTd,1PYsFXQFFOG"	"17-266-947-7315"	"ay furiously regular platelets. cou"
7912.91	"Sarabharajudara#000004211"	"GERMANY                  "	184210	"Manufacturer#4           "	"2wQRVovHrm3,v03IKzfTd,1PYsFXQFFOG"	"17-266-947-7315"	"ay furiously regular platelets. cou"
7894.56	"Sarabharajudara#000007981"	"GERMANY                  "	85472	"Manufacturer#4           "	"NSJ96vMROAbeXP"	"17-963-404-3760"	"ic platelets affix after the furiously"
7894.56	"Sarabharajudara#000007981"	"GERMANY                  "	85472	"Manufacturer#4           "	"NSJ96vMROAbeXP"	"17-963-404-3760"	"ic platelets affix after the furiously"
7887.08	"Sarabharajudara#000009792"	"GERMANY                  "	164759	"Manufacturer#3           "	"Y28ITVeYriT3kIGdV2K8fSZ V2UqT5H1Otz"	"17-988-938-4296"	"ckly around the carefully fluffy theodolites. slyly ironic pack"
7887.08	"Sarabharajudara#000009792"	"GERMANY                  "	164759	"Manufacturer#3           "	"Y28ITVeYriT3kIGdV2K8fSZ V2UqT5H1Otz"	"17-988-938-4296"	"ckly around the carefully fluffy theodolites. slyly ironic pack"
7871.50	"Sarabharajudara#000007206"	"RUSSIA                   "	104695	"Manufacturer#1           "	"3w fNCnrVmvJjE95sgWZzvW"	"32-432-452-7731"	"ironic requests. furiously final theodolites cajole. final, express packages sleep. quickly reg"
7871.50	"Sarabharajudara#000007206"	"RUSSIA                   "	104695	"Manufacturer#1           "	"3w fNCnrVmvJjE95sgWZzvW"	"32-432-452-7731"	"ironic requests. furiously final theodolites cajole. final, express packages sleep. quickly reg"
7852.45	"Sarabharajudara#000005864"	"RUSSIA                   "	8363	"Manufacturer#4           "	"WCNfBPZeSXh3h,c"	"32-454-883-3821"	"usly unusual pinto beans. brave ideas sleep carefully quickly ironi"
7852.45	"Sarabharajudara#000005864"	"RUSSIA                   "	8363	"Manufacturer#4           "	"WCNfBPZeSXh3h,c"	"32-454-883-3821"	"usly unusual pinto beans. brave ideas sleep carefully quickly ironi"
7850.66	"Sarabharajudara#000001518"	"UNITED KINGDOM           "	86501	"Manufacturer#1           "	"ONda3YJiHKJOC"	"33-730-383-3892"	"ifts haggle fluffily pending pai"
7850.66	"Sarabharajudara#000001518"	"UNITED KINGDOM           "	86501	"Manufacturer#1           "	"ONda3YJiHKJOC"	"33-730-383-3892"	"ifts haggle fluffily pending pai"
7843.52	"Sarabharajudara#000006683"	"FRANCE                   "	11680	"Manufacturer#4           "	"2Z0JGkiv01Y00oCFwUGfviIbhzCdy"	"16-464-517-8943"	" express, final pinto beans x-ray slyly asymptotes. unusual, unusual"
7843.52	"Sarabharajudara#000006683"	"FRANCE                   "	11680	"Manufacturer#4           "	"2Z0JGkiv01Y00oCFwUGfviIbhzCdy"	"16-464-517-8943"	" express, final pinto beans x-ray slyly asymptotes. unusual, unusual"
7774.62	"Sarabharajudara#000004949"	"GERMANY                  "	142434	"Manufacturer#5           "	"Rcqi8k3vuqVDrHWebhehhBl0VMFMCJV2j f"	"17-991-530-7017"	"nding deposits. final, ironic requests wake. furiously bold pin"
7774.62	"Sarabharajudara#000004949"	"GERMANY                  "	142434	"Manufacturer#5           "	"Rcqi8k3vuqVDrHWebhehhBl0VMFMCJV2j f"	"17-991-530-7017"	"nding deposits. final, ironic requests wake. furiously bold pin"
7763.74	"Sarabharajudara#000002162"	"FRANCE                   "	37155	"Manufacturer#4           "	"6ya g3MW991n9JfhxSrvgM"	"16-859-508-4893"	"eep slyly ironic accounts."
7763.74	"Sarabharajudara#000002162"	"FRANCE                   "	37155	"Manufacturer#4           "	"6ya g3MW991n9JfhxSrvgM"	"16-859-508-4893"	"eep slyly ironic accounts."
7763.74	"Sarabharajudara#000002162"	"FRANCE                   "	134622	"Manufacturer#1           "	"6ya g3MW991n9JfhxSrvgM"	"16-859-508-4893"	"eep slyly ironic accounts."
7763.74	"Sarabharajudara#000002162"	"FRANCE                   "	134622	"Manufacturer#1           "	"6ya g3MW991n9JfhxSrvgM"	"16-859-508-4893"	"eep slyly ironic accounts."
7761.36	"Sarabharajudara#000003960"	"UNITED KINGDOM           "	171442	"Manufacturer#1           "	"gTlGLliBZ5tejTU"	"33-532-108-8148"	"ep across the special deposi"
7761.36	"Sarabharajudara#000003960"	"UNITED KINGDOM           "	171442	"Manufacturer#1           "	"gTlGLliBZ5tejTU"	"33-532-108-8148"	"ep across the special deposi"
7727.83	"Sarabharajudara#000000179"	"ROMANIA                  "	100178	"Manufacturer#3           "	"d3le3XaTUC"	"29-560-587-5604"	"kages solve carefully alongside of the furiously regular patterns. blithe"
7727.83	"Sarabharajudara#000000179"	"ROMANIA                  "	100178	"Manufacturer#3           "	"d3le3XaTUC"	"29-560-587-5604"	"kages solve carefully alongside of the furiously regular patterns. blithe"
7721.78	"Sarabharajudara#000008438"	"GERMANY                  "	53427	"Manufacturer#3           "	"MHX2cideiqjxZgCyenirqSChO"	"17-510-783-5625"	"es nod slyly furiously final ideas. blithely daring packages sleep bravely f"
7721.78	"Sarabharajudara#000008438"	"GERMANY                  "	53427	"Manufacturer#3           "	"MHX2cideiqjxZgCyenirqSChO"	"17-510-783-5625"	"es nod slyly furiously final ideas. blithely daring packages sleep bravely f"
7712.45	"Sarabharajudara#000004907"	"RUSSIA                   "	72399	"Manufacturer#5           "	"77LkGSkqBmivob16KXbkuOKVdy "	"32-328-528-6335"	"y ironic ideas. furiously idle dinos use against the carefully pending waters. packages maintain a"
7712.45	"Sarabharajudara#000004907"	"RUSSIA                   "	72399	"Manufacturer#5           "	"77LkGSkqBmivob16KXbkuOKVdy "	"32-328-528-6335"	"y ironic ideas. furiously idle dinos use against the carefully pending waters. packages maintain a"
7669.38	"Sarabharajudara#000006016"	"FRANCE                   "	1015	"Manufacturer#4           "	"OmiSL2cwQ6YGQncYNAj8WZAFgz"	"16-757-121-2301"	"ffily even pinto beans grow ruthlessly pac"
7669.38	"Sarabharajudara#000006016"	"FRANCE                   "	1015	"Manufacturer#4           "	"OmiSL2cwQ6YGQncYNAj8WZAFgz"	"16-757-121-2301"	"ffily even pinto beans grow ruthlessly pac"
7627.42	"Sarabharajudara#000009880"	"FRANCE                   "	182325	"Manufacturer#3           "	"CQzqP0YiUFIvgwHsVPbbq"	"16-486-273-8984"	"structions nag quickly carefully daring requests. fluffily unusua"
7627.42	"Sarabharajudara#000009880"	"FRANCE                   "	182325	"Manufacturer#3           "	"CQzqP0YiUFIvgwHsVPbbq"	"16-486-273-8984"	"structions nag quickly carefully daring requests. fluffily unusua"
7585.24	"Sarabharajudara#000006632"	"ROMANIA                  "	111609	"Manufacturer#2           "	"TkcuZHSWRFtos 0fylpyqk"	"29-554-139-5114"	"s across the furiously sil"
7585.24	"Sarabharajudara#000006632"	"ROMANIA                  "	111609	"Manufacturer#2           "	"TkcuZHSWRFtos 0fylpyqk"	"29-554-139-5114"	"s across the furiously sil"
7469.73	"Sarabharajudara#000008756"	"ROMANIA                  "	86247	"Manufacturer#2           "	"cs50kLQEky4gv"	"29-880-355-6540"	"r requests nag against the sly"
7469.73	"Sarabharajudara#000008756"	"ROMANIA                  "	86247	"Manufacturer#2           "	"cs50kLQEky4gv"	"29-880-355-6540"	"r requests nag against the sly"
7466.57	"Sarabharajudara#000007080"	"FRANCE                   "	89555	"Manufacturer#5           "	"R1vXmHSrTAXaVu7kraZ5"	"16-957-468-4227"	"furiously quick platelets. carefully regular theodolites sleep a"
7466.57	"Sarabharajudara#000007080"	"FRANCE                   "	89555	"Manufacturer#5           "	"R1vXmHSrTAXaVu7kraZ5"	"16-957-468-4227"	"furiously quick platelets. carefully regular theodolites sleep a"
7444.01	"Sarabharajudara#000001883"	"ROMANIA                  "	89374	"Manufacturer#1           "	"H0WkWfpMkORknSj4jveLNr4YH6Yonp"	"29-825-969-2240"	" against the blithely final pinto beans. courts affix quic"
7444.01	"Sarabharajudara#000001883"	"ROMANIA                  "	89374	"Manufacturer#1           "	"H0WkWfpMkORknSj4jveLNr4YH6Yonp"	"29-825-969-2240"	" against the blithely final pinto beans. courts affix quic"
7438.01	"Sarabharajudara#000006781"	"FRANCE                   "	191742	"Manufacturer#4           "	"yq0CkqVOtfZqGGto9RnU2LncAfB5Mj6fTP,0I1sn"	"16-273-828-1660"	"are blithely silent instructions. carefully even instructions"
7438.01	"Sarabharajudara#000006781"	"FRANCE                   "	191742	"Manufacturer#4           "	"yq0CkqVOtfZqGGto9RnU2LncAfB5Mj6fTP,0I1sn"	"16-273-828-1660"	"are blithely silent instructions. carefully even instructions"
7392.78	"Sarabharajudara#000000170"	"UNITED KINGDOM           "	120169	"Manufacturer#4           "	"RtsXQ,SunkA XHy9"	"33-803-340-5398"	"ake carefully across the quickly"
7392.78	"Sarabharajudara#000000170"	"UNITED KINGDOM           "	120169	"Manufacturer#4           "	"RtsXQ,SunkA XHy9"	"33-803-340-5398"	"ake carefully across the quickly"
7385.05	"Sarabharajudara#000009959"	"UNITED KINGDOM           "	4958	"Manufacturer#4           "	"HUAzfsJeRbMc1leYMY"	"33-638-887-9523"	"ve to nag alongside of the bold, final instructions. dependencies boost. slyly fluffy accounts "
7385.05	"Sarabharajudara#000009959"	"UNITED KINGDOM           "	4958	"Manufacturer#4           "	"HUAzfsJeRbMc1leYMY"	"33-638-887-9523"	"ve to nag alongside of the bold, final instructions. dependencies boost. slyly fluffy accounts "
7346.39	"Sarabharajudara#000003467"	"GERMANY                  "	123466	"Manufacturer#1           "	"p6DZOiOzk3cXG5cx57mElGRuIPMGD1Le 0zuwqF"	"17-726-314-1724"	"ic packages run finally. blithely regular sheaves cajole quickly across the quickly even ac"
7346.39	"Sarabharajudara#000003467"	"GERMANY                  "	123466	"Manufacturer#1           "	"p6DZOiOzk3cXG5cx57mElGRuIPMGD1Le 0zuwqF"	"17-726-314-1724"	"ic packages run finally. blithely regular sheaves cajole quickly across the quickly even ac"
7323.65	"Sarabharajudara#000006595"	"GERMANY                  "	34091	"Manufacturer#1           "	"lwibmHh DJcmwev5BxgqDtlBE82keiFxRJH5Q"	"17-920-614-7661"	"quickly. final, final excuses sleep fluffily above the slyly fi"
7323.65	"Sarabharajudara#000006595"	"GERMANY                  "	34091	"Manufacturer#1           "	"lwibmHh DJcmwev5BxgqDtlBE82keiFxRJH5Q"	"17-920-614-7661"	"quickly. final, final excuses sleep fluffily above the slyly fi"
7299.85	"Sarabharajudara#000003751"	"ROMANIA                  "	38744	"Manufacturer#5           "	" 2oTtXQ7M,"	"29-278-905-7511"	"kages; finally express requests sleep furiously after the blithely regular deposits. carefully "
7299.85	"Sarabharajudara#000003751"	"ROMANIA                  "	38744	"Manufacturer#5           "	" 2oTtXQ7M,"	"29-278-905-7511"	"kages; finally express requests sleep furiously after the blithely regular deposits. carefully "
7286.94	"Sarabharajudara#000001672"	"GERMANY                  "	176637	"Manufacturer#1           "	"eWGLmD19vbE38Wu80O0Uz"	"17-914-195-9061"	" braids. slyly ironic instructions integrate blithely. slyly ironic accounts boost. carefull"
7286.94	"Sarabharajudara#000001672"	"GERMANY                  "	176637	"Manufacturer#1           "	"eWGLmD19vbE38Wu80O0Uz"	"17-914-195-9061"	" braids. slyly ironic instructions integrate blithely. slyly ironic accounts boost. carefull"
7241.31	"Sarabharajudara#000000809"	"RUSSIA                   "	80808	"Manufacturer#1           "	"dPqPaxh,IbS"	"32-172-990-2830"	" accounts. express dolphin"
7241.31	"Sarabharajudara#000000809"	"RUSSIA                   "	80808	"Manufacturer#1           "	"dPqPaxh,IbS"	"32-172-990-2830"	" accounts. express dolphin"
7174.74	"Sarabharajudara#000000085"	"GERMANY                  "	142542	"Manufacturer#3           "	"Ckls9RtlzKSF"	"17-167-806-8199"	"egular packages. bold pinto beans wake fur"
7174.74	"Sarabharajudara#000000085"	"GERMANY                  "	142542	"Manufacturer#3           "	"Ckls9RtlzKSF"	"17-167-806-8199"	"egular packages. bold pinto beans wake fur"
7174.74	"Sarabharajudara#000000085"	"GERMANY                  "	147570	"Manufacturer#5           "	"Ckls9RtlzKSF"	"17-167-806-8199"	"egular packages. bold pinto beans wake fur"
7174.74	"Sarabharajudara#000000085"	"GERMANY                  "	147570	"Manufacturer#5           "	"Ckls9RtlzKSF"	"17-167-806-8199"	"egular packages. bold pinto beans wake fur"
7148.26	"Sarabharajudara#000005680"	"UNITED KINGDOM           "	5679	"Manufacturer#3           "	"hWkoAtOkvn"	"33-547-203-1846"	"d, even ideas sleep slyly. silent"
7148.26	"Sarabharajudara#000005680"	"UNITED KINGDOM           "	5679	"Manufacturer#3           "	"hWkoAtOkvn"	"33-547-203-1846"	"d, even ideas sleep slyly. silent"
7135.82	"Sarabharajudara#000009338"	"GERMANY                  "	89337	"Manufacturer#5           "	"m3ElPvJHfvIbyFjbTGR6b"	"17-985-253-5364"	"ronic accounts cajole carefully"
7135.82	"Sarabharajudara#000009338"	"GERMANY                  "	89337	"Manufacturer#5           "	"m3ElPvJHfvIbyFjbTGR6b"	"17-985-253-5364"	"ronic accounts cajole carefully"
6990.37	"Sarabharajudara#000003417"	"UNITED KINGDOM           "	53416	"Manufacturer#1           "	"tVqlkOTDe5dtnj7CcPPJfKoSKKCp1VprhK5q7"	"33-335-458-8687"	" nag according to the silent, regular dependencies. quickly i"
6990.37	"Sarabharajudara#000003417"	"UNITED KINGDOM           "	53416	"Manufacturer#1           "	"tVqlkOTDe5dtnj7CcPPJfKoSKKCp1VprhK5q7"	"33-335-458-8687"	" nag according to the silent, regular dependencies. quickly i"
6990.37	"Sarabharajudara#000003417"	"UNITED KINGDOM           "	60910	"Manufacturer#5           "	"tVqlkOTDe5dtnj7CcPPJfKoSKKCp1VprhK5q7"	"33-335-458-8687"	" nag according to the silent, regular dependencies. quickly i"
6990.37	"Sarabharajudara#000003417"	"UNITED KINGDOM           "	60910	"Manufacturer#5           "	"tVqlkOTDe5dtnj7CcPPJfKoSKKCp1VprhK5q7"	"33-335-458-8687"	" nag according to the silent, regular dependencies. quickly i"
6988.38	"Sarabharajudara#000000606"	"ROMANIA                  "	100605	"Manufacturer#1           "	"n,iOFy5X,4GFeXNrCCKBmHucz1"	"29-856-255-1441"	"es haggle across the carefully even accounts: unusual instructions x-ray carefully. blit"
6988.38	"Sarabharajudara#000000606"	"ROMANIA                  "	100605	"Manufacturer#1           "	"n,iOFy5X,4GFeXNrCCKBmHucz1"	"29-856-255-1441"	"es haggle across the carefully even accounts: unusual instructions x-ray carefully. blit"
6955.39	"Sarabharajudara#000003665"	"ROMANIA                  "	21162	"Manufacturer#4           "	"vQEsRjcsJukdwIQ6F7A0g8WYj74LNFMu"	"29-931-790-4275"	"eposits play furiously ideas. th"
6955.39	"Sarabharajudara#000003665"	"ROMANIA                  "	21162	"Manufacturer#4           "	"vQEsRjcsJukdwIQ6F7A0g8WYj74LNFMu"	"29-931-790-4275"	"eposits play furiously ideas. th"
6950.24	"Sarabharajudara#000002703"	"FRANCE                   "	137676	"Manufacturer#4           "	"IiqJmsfyVQo"	"16-340-123-9930"	"s. packages maintain furiously final, regular requests. carefully special excuses"
6950.24	"Sarabharajudara#000002703"	"FRANCE                   "	137676	"Manufacturer#4           "	"IiqJmsfyVQo"	"16-340-123-9930"	"s. packages maintain furiously final, regular requests. carefully special excuses"
6950.24	"Sarabharajudara#000002703"	"FRANCE                   "	160186	"Manufacturer#5           "	"IiqJmsfyVQo"	"16-340-123-9930"	"s. packages maintain furiously final, regular requests. carefully special excuses"
6950.24	"Sarabharajudara#000002703"	"FRANCE                   "	160186	"Manufacturer#5           "	"IiqJmsfyVQo"	"16-340-123-9930"	"s. packages maintain furiously final, regular requests. carefully special excuses"
6860.29	"Sarabharajudara#000001968"	"FRANCE                   "	146939	"Manufacturer#2           "	"EpUTyZuUEb6YKRCQYhGqrp0WrsSiA"	"16-140-133-7640"	"ffix slyly after the slyly special accounts. regular ideas among the fu"
6860.29	"Sarabharajudara#000001968"	"FRANCE                   "	146939	"Manufacturer#2           "	"EpUTyZuUEb6YKRCQYhGqrp0WrsSiA"	"16-140-133-7640"	"ffix slyly after the slyly special accounts. regular ideas among the fu"
6841.61	"Sarabharajudara#000001130"	"RUSSIA                   "	66117	"Manufacturer#1           "	"gaw3h9cwNJTDhzgND3Ivew9mM"	"32-181-510-9827"	"nto beans. regular theodolites haggle carefully dogged accounts. u"
6841.61	"Sarabharajudara#000001130"	"RUSSIA                   "	66117	"Manufacturer#1           "	"gaw3h9cwNJTDhzgND3Ivew9mM"	"32-181-510-9827"	"nto beans. regular theodolites haggle carefully dogged accounts. u"
6833.75	"Sarabharajudara#000005607"	"ROMANIA                  "	18103	"Manufacturer#3           "	"6L4hLpnMRj"	"29-351-566-4076"	"ly across the quickly final platelets. express requests in place of the r"
6833.75	"Sarabharajudara#000005607"	"ROMANIA                  "	18103	"Manufacturer#3           "	"6L4hLpnMRj"	"29-351-566-4076"	"ly across the quickly final platelets. express requests in place of the r"
6823.45	"Sarabharajudara#000006001"	"RUSSIA                   "	68482	"Manufacturer#2           "	"6S RG2sY99qt8Am ZugMI1,Rvcbl"	"32-686-776-1548"	"ts sleep carefully. carefully even instru"
6823.45	"Sarabharajudara#000006001"	"RUSSIA                   "	68482	"Manufacturer#2           "	"6S RG2sY99qt8Am ZugMI1,Rvcbl"	"32-686-776-1548"	"ts sleep carefully. carefully even instru"
6820.97	"Sarabharajudara#000002845"	"UNITED KINGDOM           "	160328	"Manufacturer#1           "	"ZOlKEPI,8ftemk3cAGokylKstRcZiBT0sc"	"33-639-575-6452"	" furiously ironic requests. carefully final pinto beans after the blithely ironic orbi"
6820.97	"Sarabharajudara#000002845"	"UNITED KINGDOM           "	160328	"Manufacturer#1           "	"ZOlKEPI,8ftemk3cAGokylKstRcZiBT0sc"	"33-639-575-6452"	" furiously ironic requests. carefully final pinto beans after the blithely ironic orbi"
6808.81	"Sarabharajudara#000006467"	"RUSSIA                   "	183948	"Manufacturer#5           "	"SrIv,c4Ikw2Cz6tlOrM Ek1XMR"	"32-518-126-6211"	"furiously. final, final instructions sleep slyly regular, ironic in"
6808.81	"Sarabharajudara#000006467"	"RUSSIA                   "	183948	"Manufacturer#5           "	"SrIv,c4Ikw2Cz6tlOrM Ek1XMR"	"32-518-126-6211"	"furiously. final, final instructions sleep slyly regular, ironic in"
6806.27	"Sarabharajudara#000004258"	"UNITED KINGDOM           "	124257	"Manufacturer#2           "	"oXKtTTKlpcYIbuiMgfnP0sWD2P2Ngas"	"33-173-309-5477"	". ironic, even requests above the regular, final"
6806.27	"Sarabharajudara#000004258"	"UNITED KINGDOM           "	124257	"Manufacturer#2           "	"oXKtTTKlpcYIbuiMgfnP0sWD2P2Ngas"	"33-173-309-5477"	". ironic, even requests above the regular, final"
6806.27	"Sarabharajudara#000004258"	"UNITED KINGDOM           "	149229	"Manufacturer#1           "	"oXKtTTKlpcYIbuiMgfnP0sWD2P2Ngas"	"33-173-309-5477"	". ironic, even requests above the regular, final"
6806.27	"Sarabharajudara#000004258"	"UNITED KINGDOM           "	149229	"Manufacturer#1           "	"oXKtTTKlpcYIbuiMgfnP0sWD2P2Ngas"	"33-173-309-5477"	". ironic, even requests above the regular, final"
6778.63	"Sarabharajudara#000008421"	"FRANCE                   "	160872	"Manufacturer#4           "	"x2sr5EHkwDOimr0n9uWd,cDEXyIEXngBLI"	"16-554-443-4756"	" according to the pinto beans use above the carefully ironic foxes. pinto beans na"
6778.63	"Sarabharajudara#000008421"	"FRANCE                   "	160872	"Manufacturer#4           "	"x2sr5EHkwDOimr0n9uWd,cDEXyIEXngBLI"	"16-554-443-4756"	" according to the pinto beans use above the carefully ironic foxes. pinto beans na"
6774.22	"Sarabharajudara#000008330"	"GERMANY                  "	93311	"Manufacturer#1           "	"i,9fo6W58P09vbUIdNu"	"17-521-991-2604"	" are silently. slyly ironic tithes promise daringly across"
6774.22	"Sarabharajudara#000008330"	"GERMANY                  "	93311	"Manufacturer#1           "	"i,9fo6W58P09vbUIdNu"	"17-521-991-2604"	" are silently. slyly ironic tithes promise daringly across"
6742.37	"Sarabharajudara#000004519"	"FRANCE                   "	109498	"Manufacturer#3           "	"Z3Ak,pdQgQeaf5ni"	"16-984-534-8641"	"ites. final requests are. express, ironic foxes unwind slyly regular deposits. furiously ironic r"
6742.37	"Sarabharajudara#000004519"	"FRANCE                   "	109498	"Manufacturer#3           "	"Z3Ak,pdQgQeaf5ni"	"16-984-534-8641"	"ites. final requests are. express, ironic foxes unwind slyly regular deposits. furiously ironic r"
6668.15	"Sarabharajudara#000009049"	"UNITED KINGDOM           "	169048	"Manufacturer#2           "	"g4dvfWujwb"	"33-903-164-9041"	"ependencies are carefully around the ironic foxes. regular, pending packages wake car"
6668.15	"Sarabharajudara#000009049"	"UNITED KINGDOM           "	169048	"Manufacturer#2           "	"g4dvfWujwb"	"33-903-164-9041"	"ependencies are carefully around the ironic foxes. regular, pending packages wake car"
6611.85	"Sarabharajudara#000001189"	"GERMANY                  "	126164	"Manufacturer#2           "	"xYOLJtZstk3lh 2O8H231cTkSQ8rKbNCC,i9vZY"	"17-828-994-2511"	"ithely even platelets. quickly express packages boost. slyly regular deposits above th"
6611.85	"Sarabharajudara#000001189"	"GERMANY                  "	126164	"Manufacturer#2           "	"xYOLJtZstk3lh 2O8H231cTkSQ8rKbNCC,i9vZY"	"17-828-994-2511"	"ithely even platelets. quickly express packages boost. slyly regular deposits above th"
6565.69	"Sarabharajudara#000001644"	"ROMANIA                  "	121643	"Manufacturer#2           "	"ChjhHjLPsOyLPxmE"	"29-474-678-9070"	"furiously unusual pinto beans: final pinto beans wake furiously above the packages. account"
6565.69	"Sarabharajudara#000001644"	"ROMANIA                  "	121643	"Manufacturer#2           "	"ChjhHjLPsOyLPxmE"	"29-474-678-9070"	"furiously unusual pinto beans: final pinto beans wake furiously above the packages. account"
6519.54	"Sarabharajudara#000007560"	"ROMANIA                  "	87559	"Manufacturer#2           "	"ys4A6CGsNL K,9gNPx2MNnG"	"29-721-141-7530"	" carefully ironic hockey players. blithely permanent accounts wake slyly among the clo"
6519.54	"Sarabharajudara#000007560"	"ROMANIA                  "	87559	"Manufacturer#2           "	"ys4A6CGsNL K,9gNPx2MNnG"	"29-721-141-7530"	" carefully ironic hockey players. blithely permanent accounts wake slyly among the clo"
6505.25	"Sarabharajudara#000009747"	"ROMANIA                  "	189746	"Manufacturer#5           "	"jdub6FZMEJIwV3uO"	"29-910-833-4121"	"nts are furiously. blithely unusual requests accordin"
6505.25	"Sarabharajudara#000009747"	"ROMANIA                  "	189746	"Manufacturer#5           "	"jdub6FZMEJIwV3uO"	"29-910-833-4121"	"nts are furiously. blithely unusual requests accordin"
6502.62	"Sarabharajudara#000008632"	"ROMANIA                  "	48631	"Manufacturer#5           "	"QqHtvzhTWJlr7SJm1n,bqauRGd5XFIlO"	"29-543-253-5866"	" deposits cajole fluffily ironic packages. furio"
6502.62	"Sarabharajudara#000008632"	"ROMANIA                  "	48631	"Manufacturer#5           "	"QqHtvzhTWJlr7SJm1n,bqauRGd5XFIlO"	"29-543-253-5866"	" deposits cajole fluffily ironic packages. furio"
6498.51	"Sarabharajudara#000005494"	"RUSSIA                   "	125493	"Manufacturer#2           "	"u5ylCpj7F7mjMz4uXcDdE,n"	"32-569-869-5188"	"l requests haggle according to the furiously unusual inst"
6498.51	"Sarabharajudara#000005494"	"RUSSIA                   "	125493	"Manufacturer#2           "	"u5ylCpj7F7mjMz4uXcDdE,n"	"32-569-869-5188"	"l requests haggle according to the furiously unusual inst"
6449.93	"Sarabharajudara#000002940"	"GERMANY                  "	67927	"Manufacturer#1           "	"kCNPx,OJnJWYi6qd32vGytk"	"17-935-264-7724"	"ross the accounts. final requests use. regular, bold instruc"
6449.93	"Sarabharajudara#000002940"	"GERMANY                  "	67927	"Manufacturer#1           "	"kCNPx,OJnJWYi6qd32vGytk"	"17-935-264-7724"	"ross the accounts. final requests use. regular, bold instruc"
6427.20	"Sarabharajudara#000004682"	"ROMANIA                  "	182163	"Manufacturer#5           "	"VtLISnpYihV3"	"29-319-528-9629"	"iously bold dependencies. quickly pending packages detect careful"
6427.20	"Sarabharajudara#000004682"	"ROMANIA                  "	182163	"Manufacturer#5           "	"VtLISnpYihV3"	"29-319-528-9629"	"iously bold dependencies. quickly pending packages detect careful"
6361.52	"Sarabharajudara#000002185"	"ROMANIA                  "	94657	"Manufacturer#2           "	"ir25hJO802yN19NjyXPwlDf5"	"29-142-107-3683"	"e carefully bold accounts. even accounts nag quickly past the carefu"
6361.52	"Sarabharajudara#000002185"	"ROMANIA                  "	94657	"Manufacturer#2           "	"ir25hJO802yN19NjyXPwlDf5"	"29-142-107-3683"	"e carefully bold accounts. even accounts nag quickly past the carefu"
6332.07	"Sarabharajudara#000007038"	"FRANCE                   "	2037	"Manufacturer#1           "	"Z5UML Yd8ZOMvawM6dv rQFFZr,Lm"	"16-978-492-1589"	"usual asymptotes. regular deposits haggle always quickly special packages. furiously bold pack"
6332.07	"Sarabharajudara#000007038"	"FRANCE                   "	2037	"Manufacturer#1           "	"Z5UML Yd8ZOMvawM6dv rQFFZr,Lm"	"16-978-492-1589"	"usual asymptotes. regular deposits haggle always quickly special packages. furiously bold pack"
6273.03	"Sarabharajudara#000002179"	"FRANCE                   "	119667	"Manufacturer#1           "	"1bSbNinI5914UbVpjbR8"	"16-270-342-6959"	" express dependencies. unusual deposits should have to wake blithely final requests. fluffily regula"
6273.03	"Sarabharajudara#000002179"	"FRANCE                   "	119667	"Manufacturer#1           "	"1bSbNinI5914UbVpjbR8"	"16-270-342-6959"	" express dependencies. unusual deposits should have to wake blithely final requests. fluffily regula"
6222.66	"Sarabharajudara#000003639"	"ROMANIA                  "	141124	"Manufacturer#4           "	"WD22esS63VSd806yKIIbtur7izOo0"	"29-131-308-1571"	"ic, even packages among the regular instructions sleep carefully even accounts. sl"
6222.66	"Sarabharajudara#000003639"	"ROMANIA                  "	141124	"Manufacturer#4           "	"WD22esS63VSd806yKIIbtur7izOo0"	"29-131-308-1571"	"ic, even packages among the regular instructions sleep carefully even accounts. sl"
6214.16	"Sarabharajudara#000003053"	"UNITED KINGDOM           "	10551	"Manufacturer#2           "	"EVzC xEU8hGQ1rTnsO"	"33-265-220-3273"	"rint blithely carefully regular accounts. slowly bold asymptotes are above the sl"
6214.16	"Sarabharajudara#000003053"	"UNITED KINGDOM           "	10551	"Manufacturer#2           "	"EVzC xEU8hGQ1rTnsO"	"33-265-220-3273"	"rint blithely carefully regular accounts. slowly bold asymptotes are above the sl"
6206.46	"Sarabharajudara#000001133"	"UNITED KINGDOM           "	71132	"Manufacturer#5           "	"cnqLejGYqbqrMVlxNiaY,JdcqQkHFYeyfum2Nv1w"	"33-858-158-1956"	"lithely bold requests nag. regular, even requests integrate. requests cajole s"
6206.46	"Sarabharajudara#000001133"	"UNITED KINGDOM           "	71132	"Manufacturer#5           "	"cnqLejGYqbqrMVlxNiaY,JdcqQkHFYeyfum2Nv1w"	"33-858-158-1956"	"lithely bold requests nag. regular, even requests integrate. requests cajole s"
6206.46	"Sarabharajudara#000001133"	"UNITED KINGDOM           "	163584	"Manufacturer#5           "	"cnqLejGYqbqrMVlxNiaY,JdcqQkHFYeyfum2Nv1w"	"33-858-158-1956"	"lithely bold requests nag. regular, even requests integrate. requests cajole s"
6206.46	"Sarabharajudara#000001133"	"UNITED KINGDOM           "	163584	"Manufacturer#5           "	"cnqLejGYqbqrMVlxNiaY,JdcqQkHFYeyfum2Nv1w"	"33-858-158-1956"	"lithely bold requests nag. regular, even requests integrate. requests cajole s"
6183.73	"Sarabharajudara#000007066"	"FRANCE                   "	32059	"Manufacturer#1           "	"a rdeYnN1ELxIjkkCRo4UVbJqh2lXmQB2TXBuwPw"	"16-880-494-3956"	"mold furiously. regular packages are furiously. asymptotes cajole quickly after t"
6183.73	"Sarabharajudara#000007066"	"FRANCE                   "	32059	"Manufacturer#1           "	"a rdeYnN1ELxIjkkCRo4UVbJqh2lXmQB2TXBuwPw"	"16-880-494-3956"	"mold furiously. regular packages are furiously. asymptotes cajole quickly after t"
6174.29	"Sarabharajudara#000003630"	"FRANCE                   "	178595	"Manufacturer#1           "	"x YhwKhY,c1A"	"16-376-892-5137"	"r accounts haggle slyly even accou"
6174.29	"Sarabharajudara#000003630"	"FRANCE                   "	178595	"Manufacturer#1           "	"x YhwKhY,c1A"	"16-376-892-5137"	"r accounts haggle slyly even accou"
6158.33	"Sarabharajudara#000006787"	"GERMANY                  "	66786	"Manufacturer#1           "	"uc7YzttoH5LKqbaQSKsX"	"17-353-912-8165"	"gle among the furiously final"
6158.33	"Sarabharajudara#000006787"	"GERMANY                  "	66786	"Manufacturer#1           "	"uc7YzttoH5LKqbaQSKsX"	"17-353-912-8165"	"gle among the furiously final"
6145.42	"Sarabharajudara#000001818"	"GERMANY                  "	106797	"Manufacturer#4           "	"CMzzFu9R7w"	"17-152-692-4204"	"ronic pinto beans haggle quickly. slyly pending Tiresias breach furiously. blit"
6145.42	"Sarabharajudara#000001818"	"GERMANY                  "	106797	"Manufacturer#4           "	"CMzzFu9R7w"	"17-152-692-4204"	"ronic pinto beans haggle quickly. slyly pending Tiresias breach furiously. blit"
6124.81	"Sarabharajudara#000001300"	"UNITED KINGDOM           "	193742	"Manufacturer#1           "	"UqX4pArRmxHi3LSB"	"33-890-567-7030"	"counts sleep regular theodolite"
6124.81	"Sarabharajudara#000001300"	"UNITED KINGDOM           "	193742	"Manufacturer#1           "	"UqX4pArRmxHi3LSB"	"33-890-567-7030"	"counts sleep regular theodolite"
6107.04	"Sarabharajudara#000007163"	"RUSSIA                   "	69644	"Manufacturer#5           "	"9jzdDoHPLZ6gMt7GzSLqP Sdn10zYViXoNTT8XO"	"32-457-558-8569"	"sts are. instructions sleep carefully across the ironic foxes. carefully qu"
6107.04	"Sarabharajudara#000007163"	"RUSSIA                   "	69644	"Manufacturer#5           "	"9jzdDoHPLZ6gMt7GzSLqP Sdn10zYViXoNTT8XO"	"32-457-558-8569"	"sts are. instructions sleep carefully across the ironic foxes. carefully qu"
6071.58	"Sarabharajudara#000000605"	"FRANCE                   "	23098	"Manufacturer#5           "	"wdwiNoNT8pVHOTHQ8jhVzaOTkU"	"16-835-870-9488"	"foxes poach blithely beneath the excuses: ironic multipliers haggle quickly furiously unu"
6071.58	"Sarabharajudara#000000605"	"FRANCE                   "	23098	"Manufacturer#5           "	"wdwiNoNT8pVHOTHQ8jhVzaOTkU"	"16-835-870-9488"	"foxes poach blithely beneath the excuses: ironic multipliers haggle quickly furiously unu"
6044.11	"Sarabharajudara#000005051"	"RUSSIA                   "	77529	"Manufacturer#1           "	"Puejq3pV,JFX4,hUnhHbr"	"32-592-547-7141"	"ts. slyly pending instructions boost furiously. slyl"
6044.11	"Sarabharajudara#000005051"	"RUSSIA                   "	77529	"Manufacturer#1           "	"Puejq3pV,JFX4,hUnhHbr"	"32-592-547-7141"	"ts. slyly pending instructions boost furiously. slyl"
6029.14	"Sarabharajudara#000002321"	"ROMANIA                  "	7320	"Manufacturer#5           "	"0FWKkhdhrSNpN3ql"	"29-805-994-2628"	"l ideas. furiously ironic accounts sleep. iron"
6029.14	"Sarabharajudara#000002321"	"ROMANIA                  "	7320	"Manufacturer#5           "	"0FWKkhdhrSNpN3ql"	"29-805-994-2628"	"l ideas. furiously ironic accounts sleep. iron"
6020.98	"Sarabharajudara#000003870"	"UNITED KINGDOM           "	158839	"Manufacturer#1           "	"Q8mzUM5BaMsDOolmRXuAIhwY"	"33-796-500-2325"	"y express accounts wake around the quickly ironic asymptotes. regula"
6020.98	"Sarabharajudara#000003870"	"UNITED KINGDOM           "	158839	"Manufacturer#1           "	"Q8mzUM5BaMsDOolmRXuAIhwY"	"33-796-500-2325"	"y express accounts wake around the quickly ironic asymptotes. regula"
6016.26	"Sarabharajudara#000009281"	"FRANCE                   "	121744	"Manufacturer#4           "	"3zaUojlR0cW5hXNbJEHL1Dp0u lo9W,m6msg"	"16-427-709-3910"	"iments are quickly according to the regular, silent ideas. fluffi"
6016.26	"Sarabharajudara#000009281"	"FRANCE                   "	121744	"Manufacturer#4           "	"3zaUojlR0cW5hXNbJEHL1Dp0u lo9W,m6msg"	"16-427-709-3910"	"iments are quickly according to the regular, silent ideas. fluffi"
5961.20	"Sarabharajudara#000007305"	"GERMANY                  "	64798	"Manufacturer#4           "	"pFuKnETctQn1J"	"17-698-827-9966"	"ffix fluffily bold, final packages. quickly expr"
5961.20	"Sarabharajudara#000007305"	"GERMANY                  "	64798	"Manufacturer#4           "	"pFuKnETctQn1J"	"17-698-827-9966"	"ffix fluffily bold, final packages. quickly expr"
5929.82	"Sarabharajudara#000001576"	"FRANCE                   "	59070	"Manufacturer#3           "	"3dj4fsF5fNQ2boo1riXOA7N9t"	"16-116-644-2882"	"ic accounts cajole slyly ironic accounts. pe"
5929.82	"Sarabharajudara#000001576"	"FRANCE                   "	59070	"Manufacturer#3           "	"3dj4fsF5fNQ2boo1riXOA7N9t"	"16-116-644-2882"	"ic accounts cajole slyly ironic accounts. pe"
5866.79	"Sarabharajudara#000002086"	"UNITED KINGDOM           "	107065	"Manufacturer#2           "	" ,yBCAhvKWP21ZO1d94zY2Rcl46Z"	"33-257-695-7480"	"e quickly silent foxes impress regular, bold instructions. carefully enticing deposits along t"
5866.79	"Sarabharajudara#000002086"	"UNITED KINGDOM           "	107065	"Manufacturer#2           "	" ,yBCAhvKWP21ZO1d94zY2Rcl46Z"	"33-257-695-7480"	"e quickly silent foxes impress regular, bold instructions. carefully enticing deposits along t"
5851.59	"Sarabharajudara#000001520"	"ROMANIA                  "	81519	"Manufacturer#4           "	"wfx,kh4HNP"	"29-367-271-5757"	"s nag furiously around the special, regular deposits. sl"
5851.59	"Sarabharajudara#000001520"	"ROMANIA                  "	81519	"Manufacturer#4           "	"wfx,kh4HNP"	"29-367-271-5757"	"s nag furiously around the special, regular deposits. sl"
5832.40	"Sarabharajudara#000004167"	"ROMANIA                  "	166618	"Manufacturer#3           "	"ZeTibFfxIahMkQSCmlxk 2zJYiSQOaR"	"29-842-894-8667"	"even instructions above the braids doubt carefully across the blithe pinto beans. "
5832.40	"Sarabharajudara#000004167"	"ROMANIA                  "	166618	"Manufacturer#3           "	"ZeTibFfxIahMkQSCmlxk 2zJYiSQOaR"	"29-842-894-8667"	"even instructions above the braids doubt carefully across the blithe pinto beans. "
5826.08	"Sarabharajudara#000006524"	"ROMANIA                  "	49011	"Manufacturer#5           "	"eaGKaiQ6KIdx"	"29-380-982-1928"	"thely blithely express deposits."
5826.08	"Sarabharajudara#000006524"	"ROMANIA                  "	49011	"Manufacturer#5           "	"eaGKaiQ6KIdx"	"29-380-982-1928"	"thely blithely express deposits."
5801.24	"Sarabharajudara#000006544"	"FRANCE                   "	74036	"Manufacturer#3           "	"1yFDGy78U3qRK2fq1S"	"16-777-983-3958"	"sly regular requests about the pending instructions haggle around the slyly pending reques"
5801.24	"Sarabharajudara#000006544"	"FRANCE                   "	74036	"Manufacturer#3           "	"1yFDGy78U3qRK2fq1S"	"16-777-983-3958"	"sly regular requests about the pending instructions haggle around the slyly pending reques"
5800.50	"Sarabharajudara#000001376"	"FRANCE                   "	13872	"Manufacturer#3           "	"RRPIyyvGjLfRy20DmcdsEl6"	"16-127-723-7329"	"final accounts maintain carefully final deposits; stealthily bold theodolites "
5800.50	"Sarabharajudara#000001376"	"FRANCE                   "	13872	"Manufacturer#3           "	"RRPIyyvGjLfRy20DmcdsEl6"	"16-127-723-7329"	"final accounts maintain carefully final deposits; stealthily bold theodolites "
5730.52	"Sarabharajudara#000001468"	"UNITED KINGDOM           "	33958	"Manufacturer#1           "	"IfGLGB5BHW"	"33-379-279-9526"	" quickly pending foxes. regular decoys are car"
5730.52	"Sarabharajudara#000001468"	"UNITED KINGDOM           "	33958	"Manufacturer#1           "	"IfGLGB5BHW"	"33-379-279-9526"	" quickly pending foxes. regular decoys are car"
5727.03	"Sarabharajudara#000001185"	"UNITED KINGDOM           "	6184	"Manufacturer#5           "	"khazl747u4Qc4h,OL4BqmkEH4LzrmDsu6vq"	"33-194-433-6517"	"al requests. furiously regular ideas are. quickly"
5727.03	"Sarabharajudara#000001185"	"UNITED KINGDOM           "	6184	"Manufacturer#5           "	"khazl747u4Qc4h,OL4BqmkEH4LzrmDsu6vq"	"33-194-433-6517"	"al requests. furiously regular ideas are. quickly"
5722.22	"Sarabharajudara#000001675"	"UNITED KINGDOM           "	111674	"Manufacturer#1           "	"ivZoa,172A5gp4dgA93YI6l96Ksh5XkKeEcy0C"	"33-133-387-6972"	"fter the requests. even foxes affix carefully after the blithely "
5722.22	"Sarabharajudara#000001675"	"UNITED KINGDOM           "	111674	"Manufacturer#1           "	"ivZoa,172A5gp4dgA93YI6l96Ksh5XkKeEcy0C"	"33-133-387-6972"	"fter the requests. even foxes affix carefully after the blithely "
5675.39	"Sarabharajudara#000004335"	"UNITED KINGDOM           "	169302	"Manufacturer#1           "	"sLgbkSGstpaB"	"33-111-821-7078"	"its. regular warthogs cajole whit"
5675.39	"Sarabharajudara#000004335"	"UNITED KINGDOM           "	169302	"Manufacturer#1           "	"sLgbkSGstpaB"	"33-111-821-7078"	"its. regular warthogs cajole whit"
5647.88	"Sarabharajudara#000004135"	"GERMANY                  "	1634	"Manufacturer#2           "	"dbHS8xeJMoEG yEVI,eRk6LZrj 89XoJ"	"17-244-262-1877"	"lithely regular accounts against the ironically un"
5647.88	"Sarabharajudara#000004135"	"GERMANY                  "	1634	"Manufacturer#2           "	"dbHS8xeJMoEG yEVI,eRk6LZrj 89XoJ"	"17-244-262-1877"	"lithely regular accounts against the ironically un"
5630.80	"Sarabharajudara#000002692"	"FRANCE                   "	62691	"Manufacturer#4           "	"1B3q56lLAYJlOR5LGa V"	"16-399-574-8135"	"counts integrate slyly about the furiously unusual packages. final idea"
5630.80	"Sarabharajudara#000002692"	"FRANCE                   "	62691	"Manufacturer#4           "	"1B3q56lLAYJlOR5LGa V"	"16-399-574-8135"	"counts integrate slyly about the furiously unusual packages. final idea"
5621.87	"Sarabharajudara#000008447"	"UNITED KINGDOM           "	23442	"Manufacturer#2           "	"kYxlpT,F8AJgEj8uF"	"33-992-618-4096"	"tect blithely against the silent packages; final platelets accordi"
5621.87	"Sarabharajudara#000008447"	"UNITED KINGDOM           "	23442	"Manufacturer#2           "	"kYxlpT,F8AJgEj8uF"	"33-992-618-4096"	"tect blithely against the silent packages; final platelets accordi"
5621.64	"Sarabharajudara#000009241"	"RUSSIA                   "	179240	"Manufacturer#1           "	"8nrvAcXiaw0NVOKvUthGohy2T0yZQx"	"32-250-945-2444"	". carefully even requests wake. blithely bold pinto"
5621.64	"Sarabharajudara#000009241"	"RUSSIA                   "	179240	"Manufacturer#1           "	"8nrvAcXiaw0NVOKvUthGohy2T0yZQx"	"32-250-945-2444"	". carefully even requests wake. blithely bold pinto"
5613.57	"Sarabharajudara#000007193"	"FRANCE                   "	32186	"Manufacturer#2           "	"LOysL3v1UnfSXP,O3drFxmt2eCd2FCQa3"	"16-365-781-2094"	"y regular requests cajole furiously. thinly silent pinto beans "
5613.57	"Sarabharajudara#000007193"	"FRANCE                   "	32186	"Manufacturer#2           "	"LOysL3v1UnfSXP,O3drFxmt2eCd2FCQa3"	"16-365-781-2094"	"y regular requests cajole furiously. thinly silent pinto beans "
5571.81	"Sarabharajudara#000000362"	"UNITED KINGDOM           "	125337	"Manufacturer#3           "	"XdtN0U5Qm2Z"	"33-445-749-9918"	"e furiously. slowly regular accounts sleep furiously. carefully bo"
5571.81	"Sarabharajudara#000000362"	"UNITED KINGDOM           "	125337	"Manufacturer#3           "	"XdtN0U5Qm2Z"	"33-445-749-9918"	"e furiously. slowly regular accounts sleep furiously. carefully bo"
5562.66	"Sarabharajudara#000003914"	"RUSSIA                   "	116380	"Manufacturer#5           "	"uBG4kbR1mp6LQZCp6DlCmpzlw9sh2XnSPMT"	"32-389-834-9741"	" blithely ironic requests are permanent accounts. regular deposits haggle carefully"
5562.66	"Sarabharajudara#000003914"	"RUSSIA                   "	116380	"Manufacturer#5           "	"uBG4kbR1mp6LQZCp6DlCmpzlw9sh2XnSPMT"	"32-389-834-9741"	" blithely ironic requests are permanent accounts. regular deposits haggle carefully"
5557.64	"Sarabharajudara#000004192"	"GERMANY                  "	4191	"Manufacturer#3           "	"93oY1dMuRsP4aaCK0QrsoFgZf6yB9CHy2Ba"	"17-858-849-2452"	"s. blithely ironic excuses nag fluffily special pinto beans. c"
5557.64	"Sarabharajudara#000004192"	"GERMANY                  "	4191	"Manufacturer#3           "	"93oY1dMuRsP4aaCK0QrsoFgZf6yB9CHy2Ba"	"17-858-849-2452"	"s. blithely ironic excuses nag fluffily special pinto beans. c"
5438.82	"Sarabharajudara#000004618"	"FRANCE                   "	104617	"Manufacturer#3           "	"NVML8aK152LD2bR61rxd7CVY3OwLFT3yP"	"16-140-955-8584"	" even packages sublate along the regular, even accounts. r"
5438.82	"Sarabharajudara#000004618"	"FRANCE                   "	104617	"Manufacturer#3           "	"NVML8aK152LD2bR61rxd7CVY3OwLFT3yP"	"16-140-955-8584"	" even packages sublate along the regular, even accounts. r"
5402.57	"Sarabharajudara#000002533"	"FRANCE                   "	164984	"Manufacturer#1           "	"3ZSYvP04QM"	"16-751-912-9737"	"lar excuses. final packages haggle quickly about the depos"
5402.57	"Sarabharajudara#000002533"	"FRANCE                   "	164984	"Manufacturer#1           "	"3ZSYvP04QM"	"16-751-912-9737"	"lar excuses. final packages haggle quickly about the depos"
5402.57	"Sarabharajudara#000002533"	"FRANCE                   "	190013	"Manufacturer#3           "	"3ZSYvP04QM"	"16-751-912-9737"	"lar excuses. final packages haggle quickly about the depos"
5402.57	"Sarabharajudara#000002533"	"FRANCE                   "	190013	"Manufacturer#3           "	"3ZSYvP04QM"	"16-751-912-9737"	"lar excuses. final packages haggle quickly about the depos"
5389.56	"Sarabharajudara#000007697"	"FRANCE                   "	72682	"Manufacturer#5           "	"4lzQlXRJgy 9s1oDSf7yMDlotyh1qy1Wx4vLXd"	"16-123-112-2857"	"its haggle fluffily. final packages"
5389.56	"Sarabharajudara#000007697"	"FRANCE                   "	72682	"Manufacturer#5           "	"4lzQlXRJgy 9s1oDSf7yMDlotyh1qy1Wx4vLXd"	"16-123-112-2857"	"its haggle fluffily. final packages"
5379.61	"Sarabharajudara#000008620"	"GERMANY                  "	193581	"Manufacturer#1           "	"fnE6fyXgoqfP4aqx1LRbQiqYm7854p5jhuZ"	"17-623-256-9547"	"lyly busy instructions. carefu"
5379.61	"Sarabharajudara#000008620"	"GERMANY                  "	193581	"Manufacturer#1           "	"fnE6fyXgoqfP4aqx1LRbQiqYm7854p5jhuZ"	"17-623-256-9547"	"lyly busy instructions. carefu"
5368.40	"Sarabharajudara#000008837"	"RUSSIA                   "	56331	"Manufacturer#4           "	"30kMU47oW4YJyT4BokEsln"	"32-165-179-1361"	"w dependencies x-ray quickly pending decoys. furiously bold deposit"
5368.40	"Sarabharajudara#000008837"	"RUSSIA                   "	56331	"Manufacturer#4           "	"30kMU47oW4YJyT4BokEsln"	"32-165-179-1361"	"w dependencies x-ray quickly pending decoys. furiously bold deposit"
5341.10	"Sarabharajudara#000006292"	"UNITED KINGDOM           "	101271	"Manufacturer#3           "	"4W5P7Twl,0zdDFTjjYA2jxi5Zm"	"33-887-621-6202"	" regular foxes sleep carefully final deposits."
5341.10	"Sarabharajudara#000006292"	"UNITED KINGDOM           "	101271	"Manufacturer#3           "	"4W5P7Twl,0zdDFTjjYA2jxi5Zm"	"33-887-621-6202"	" regular foxes sleep carefully final deposits."
5337.68	"Sarabharajudara#000003070"	"RUSSIA                   "	53069	"Manufacturer#4           "	"F0sjr17IwdKH9B7DOZXOnM hjhOsfHy9okdsk"	"32-581-887-7880"	"nic packages among the deposits cajole according to the carefully special foxes. furiously ironic ac"
5337.68	"Sarabharajudara#000003070"	"RUSSIA                   "	53069	"Manufacturer#4           "	"F0sjr17IwdKH9B7DOZXOnM hjhOsfHy9okdsk"	"32-581-887-7880"	"nic packages among the deposits cajole according to the carefully special foxes. furiously ironic ac"
5298.86	"Sarabharajudara#000009457"	"RUSSIA                   "	119456	"Manufacturer#5           "	"7trQrMbRXGK7bUSJOpn7zYoViyi7Mzwx"	"32-502-244-5147"	"regular asymptotes wake blithely alongside of the slyly final"
5298.86	"Sarabharajudara#000009457"	"RUSSIA                   "	119456	"Manufacturer#5           "	"7trQrMbRXGK7bUSJOpn7zYoViyi7Mzwx"	"32-502-244-5147"	"regular asymptotes wake blithely alongside of the slyly final"
5274.87	"Sarabharajudara#000009479"	"ROMANIA                  "	126966	"Manufacturer#1           "	"tNBWHgO87pZu9oxZHyycVwb73syHwis64g8HLP N"	"29-321-285-3408"	"efully bold pinto beans sleep carefully about the carefully ir"
5274.87	"Sarabharajudara#000009479"	"ROMANIA                  "	126966	"Manufacturer#1           "	"tNBWHgO87pZu9oxZHyycVwb73syHwis64g8HLP N"	"29-321-285-3408"	"efully bold pinto beans sleep carefully about the carefully ir"
5233.22	"Sarabharajudara#000006295"	"ROMANIA                  "	171260	"Manufacturer#1           "	",kIChX9uLiLe2,Rt9Iyzj cZJ"	"29-927-347-5184"	"y regular requests sleep furiously regular foxes; carefully silent requests about the quickly fi"
5233.22	"Sarabharajudara#000006295"	"ROMANIA                  "	171260	"Manufacturer#1           "	",kIChX9uLiLe2,Rt9Iyzj cZJ"	"29-927-347-5184"	"y regular requests sleep furiously regular foxes; carefully silent requests about the quickly fi"
5226.05	"Sarabharajudara#000006214"	"UNITED KINGDOM           "	6213	"Manufacturer#3           "	"BWNr,0S,rs3o3vXkMtKZCT0OyS"	"33-484-970-5494"	"yly express accounts. blithely ironic excuses detect carefully outside the quickly special theodoli"
5226.05	"Sarabharajudara#000006214"	"UNITED KINGDOM           "	6213	"Manufacturer#3           "	"BWNr,0S,rs3o3vXkMtKZCT0OyS"	"33-484-970-5494"	"yly express accounts. blithely ironic excuses detect carefully outside the quickly special theodoli"
5212.36	"Sarabharajudara#000002972"	"FRANCE                   "	112971	"Manufacturer#5           "	"UV6ajsKfv3WALu2LFPFrrl3IaPPF6YtVgoyClz1i"	"16-493-546-8467"	"re quickly quick, ironic accounts? carefully unusual requests whithout the even requests use blit"
5212.36	"Sarabharajudara#000002972"	"FRANCE                   "	112971	"Manufacturer#5           "	"UV6ajsKfv3WALu2LFPFrrl3IaPPF6YtVgoyClz1i"	"16-493-546-8467"	"re quickly quick, ironic accounts? carefully unusual requests whithout the even requests use blit"
5174.82	"Sarabharajudara#000003702"	"ROMANIA                  "	191182	"Manufacturer#1           "	"HzPbcxd6nPXU4wtvM7DiPBihBCEbI6"	"29-419-845-6897"	" across the quickly pending accou"
5174.82	"Sarabharajudara#000003702"	"ROMANIA                  "	191182	"Manufacturer#1           "	"HzPbcxd6nPXU4wtvM7DiPBihBCEbI6"	"29-419-845-6897"	" across the quickly pending accou"
5174.04	"Sarabharajudara#000001829"	"ROMANIA                  "	124292	"Manufacturer#1           "	"CC3jTZymrkpJSYqh"	"29-598-220-3639"	"requests haggle furiously al"
5174.04	"Sarabharajudara#000001829"	"ROMANIA                  "	124292	"Manufacturer#1           "	"CC3jTZymrkpJSYqh"	"29-598-220-3639"	"requests haggle furiously al"
5134.08	"Sarabharajudara#000002646"	"ROMANIA                  "	45133	"Manufacturer#2           "	" ZGaGVMSy31SeBVfpf8ey8D2mm,kUbdX2SWsM"	"29-314-944-1425"	"d deposits. furiously unusual accounts are along the silent cour"
5134.08	"Sarabharajudara#000002646"	"ROMANIA                  "	45133	"Manufacturer#2           "	" ZGaGVMSy31SeBVfpf8ey8D2mm,kUbdX2SWsM"	"29-314-944-1425"	"d deposits. furiously unusual accounts are along the silent cour"
5124.70	"Sarabharajudara#000002257"	"UNITED KINGDOM           "	39753	"Manufacturer#3           "	"vbr6RiyybhW4nqIxTayAPGZnLE4zeE"	"33-304-497-5207"	"ular foxes. blithely regular accounts do"
5124.70	"Sarabharajudara#000002257"	"UNITED KINGDOM           "	39753	"Manufacturer#3           "	"vbr6RiyybhW4nqIxTayAPGZnLE4zeE"	"33-304-497-5207"	"ular foxes. blithely regular accounts do"
5110.27	"Sarabharajudara#000009645"	"GERMANY                  "	157129	"Manufacturer#3           "	"6CmMjDVLD5mzK5k19CaL"	"17-170-281-6088"	"al deposits according to the furiously final asymptotes use carefully across"
5110.27	"Sarabharajudara#000009645"	"GERMANY                  "	157129	"Manufacturer#3           "	"6CmMjDVLD5mzK5k19CaL"	"17-170-281-6088"	"al deposits according to the furiously final asymptotes use carefully across"
5060.33	"Sarabharajudara#000006875"	"FRANCE                   "	129338	"Manufacturer#5           "	"UERFmEvKRfeAsNL2tKKfWhIm2"	"16-439-339-6116"	"ronic packages. even accounts integrate blithely abo"
5060.33	"Sarabharajudara#000006875"	"FRANCE                   "	129338	"Manufacturer#5           "	"UERFmEvKRfeAsNL2tKKfWhIm2"	"16-439-339-6116"	"ronic packages. even accounts integrate blithely abo"
5041.68	"Sarabharajudara#000007092"	"RUSSIA                   "	129555	"Manufacturer#1           "	",Gjn1UH1OfR9N3xs4RCDOx4DSV67YWL"	"32-400-807-1421"	"ts. pinto beans along the furiously final instructions doze iro"
5041.68	"Sarabharajudara#000007092"	"RUSSIA                   "	129555	"Manufacturer#1           "	",Gjn1UH1OfR9N3xs4RCDOx4DSV67YWL"	"32-400-807-1421"	"ts. pinto beans along the furiously final instructions doze iro"
5041.68	"Sarabharajudara#000007092"	"RUSSIA                   "	139552	"Manufacturer#2           "	",Gjn1UH1OfR9N3xs4RCDOx4DSV67YWL"	"32-400-807-1421"	"ts. pinto beans along the furiously final instructions doze iro"
5041.68	"Sarabharajudara#000007092"	"RUSSIA                   "	139552	"Manufacturer#2           "	",Gjn1UH1OfR9N3xs4RCDOx4DSV67YWL"	"32-400-807-1421"	"ts. pinto beans along the furiously final instructions doze iro"
5008.72	"Sarabharajudara#000001506"	"ROMANIA                  "	68999	"Manufacturer#2           "	"0mjuNYVOEOzcX1EV80CX6IwlB"	"29-282-871-8851"	"jole blithely above the blithely si"
5008.72	"Sarabharajudara#000001506"	"ROMANIA                  "	68999	"Manufacturer#2           "	"0mjuNYVOEOzcX1EV80CX6IwlB"	"29-282-871-8851"	"jole blithely above the blithely si"
5001.39	"Sarabharajudara#000005747"	"ROMANIA                  "	178195	"Manufacturer#4           "	"D0gyiOCgqwi123gjTq7cQnNzLD,e16rF 8JPO"	"29-938-591-4953"	"ly even packages. theodolites x-ray quickly. carefully even packages lose furiously in"
5001.39	"Sarabharajudara#000005747"	"ROMANIA                  "	178195	"Manufacturer#4           "	"D0gyiOCgqwi123gjTq7cQnNzLD,e16rF 8JPO"	"29-938-591-4953"	"ly even packages. theodolites x-ray quickly. carefully even packages lose furiously in"
4852.77	"Sarabharajudara#000008984"	"ROMANIA                  "	13981	"Manufacturer#2           "	"Ap5g9fjZUuY0FnaRxsqaZ"	"29-569-265-6236"	"lms according to the ideas wake "
4852.77	"Sarabharajudara#000008984"	"ROMANIA                  "	13981	"Manufacturer#2           "	"Ap5g9fjZUuY0FnaRxsqaZ"	"29-569-265-6236"	"lms according to the ideas wake "
4850.96	"Sarabharajudara#000001768"	"RUSSIA                   "	119256	"Manufacturer#2           "	"Ug4jMAaK46J31Z5GFO7x"	"32-197-236-9784"	"counts. slyly even hockey players mold furiousl"
4850.96	"Sarabharajudara#000001768"	"RUSSIA                   "	119256	"Manufacturer#2           "	"Ug4jMAaK46J31Z5GFO7x"	"32-197-236-9784"	"counts. slyly even hockey players mold furiousl"
4772.19	"Sarabharajudara#000003468"	"FRANCE                   "	95940	"Manufacturer#5           "	"uauXeECdlFyj GDUl4b9YScxUAzSWY12uVP Vw B"	"16-219-806-1236"	"structions boost quickly. accounts alongside of the carefully ironic deposits sleep carefully agains"
4772.19	"Sarabharajudara#000003468"	"FRANCE                   "	95940	"Manufacturer#5           "	"uauXeECdlFyj GDUl4b9YScxUAzSWY12uVP Vw B"	"16-219-806-1236"	"structions boost quickly. accounts alongside of the carefully ironic deposits sleep carefully agains"
4742.57	"Sarabharajudara#000005901"	"FRANCE                   "	125900	"Manufacturer#1           "	"vfCFcAHhCa2WfogeAjYfZshxHQQdJ"	"16-840-687-6900"	"onic pains are blithely according to the quickly ironic instruc"
4742.57	"Sarabharajudara#000005901"	"FRANCE                   "	125900	"Manufacturer#1           "	"vfCFcAHhCa2WfogeAjYfZshxHQQdJ"	"16-840-687-6900"	"onic pains are blithely according to the quickly ironic instruc"
4702.11	"Sarabharajudara#000004404"	"GERMANY                  "	119381	"Manufacturer#5           "	"nClT5NhhPdxViApjx3ahv ryCqj7R2pj"	"17-844-693-1492"	"gle blithely final instructions. furiously silent ti"
4702.11	"Sarabharajudara#000004404"	"GERMANY                  "	119381	"Manufacturer#5           "	"nClT5NhhPdxViApjx3ahv ryCqj7R2pj"	"17-844-693-1492"	"gle blithely final instructions. furiously silent ti"
4702.11	"Sarabharajudara#000004404"	"GERMANY                  "	129379	"Manufacturer#4           "	"nClT5NhhPdxViApjx3ahv ryCqj7R2pj"	"17-844-693-1492"	"gle blithely final instructions. furiously silent ti"
4702.11	"Sarabharajudara#000004404"	"GERMANY                  "	129379	"Manufacturer#4           "	"nClT5NhhPdxViApjx3ahv ryCqj7R2pj"	"17-844-693-1492"	"gle blithely final instructions. furiously silent ti"
4696.43	"Sarabharajudara#000004166"	"RUSSIA                   "	171648	"Manufacturer#2           "	"dEGlhdQfTkadp"	"32-753-533-6531"	". carefully special accounts sleep slyly special, final pinto beans. quickly regular excuses "
4696.43	"Sarabharajudara#000004166"	"RUSSIA                   "	171648	"Manufacturer#2           "	"dEGlhdQfTkadp"	"32-753-533-6531"	". carefully special accounts sleep slyly special, final pinto beans. quickly regular excuses "
4632.40	"Sarabharajudara#000002725"	"GERMANY                  "	157694	"Manufacturer#3           "	"LoFZWIp7I4NZHNzj,n2o"	"17-827-742-4461"	" affix. express foxes nag carefully along the unusual deposits. slyly regular pinto beans"
4632.40	"Sarabharajudara#000002725"	"GERMANY                  "	157694	"Manufacturer#3           "	"LoFZWIp7I4NZHNzj,n2o"	"17-827-742-4461"	" affix. express foxes nag carefully along the unusual deposits. slyly regular pinto beans"
4627.81	"Sarabharajudara#000002319"	"FRANCE                   "	152318	"Manufacturer#3           "	"3z3bTulBgv8Re30oDzKgGlZQT"	"16-531-572-9386"	"ptotes. quickly pending foxes cajole carefully slyly silent accounts. quickly ironic instr"
4627.81	"Sarabharajudara#000002319"	"FRANCE                   "	152318	"Manufacturer#3           "	"3z3bTulBgv8Re30oDzKgGlZQT"	"16-531-572-9386"	"ptotes. quickly pending foxes cajole carefully slyly silent accounts. quickly ironic instr"
4593.60	"Sarabharajudara#000003239"	"UNITED KINGDOM           "	78224	"Manufacturer#5           "	"RRSmqHhyBHJegOW867GgvVlkE4MJ6tz6jzi6PqIO"	"33-288-804-3846"	" slyly. unusual, ironic theodolites sleep slyly across"
4593.60	"Sarabharajudara#000003239"	"UNITED KINGDOM           "	78224	"Manufacturer#5           "	"RRSmqHhyBHJegOW867GgvVlkE4MJ6tz6jzi6PqIO"	"33-288-804-3846"	" slyly. unusual, ironic theodolites sleep slyly across"
4582.83	"Sarabharajudara#000006753"	"FRANCE                   "	36752	"Manufacturer#5           "	"vkoG26rE,dMq6n5 1tmQOW2wrU,xyXEahegZN,"	"16-508-617-7667"	"unusual instructions according to the blithely pending excuses are about the accounts. express,"
4582.83	"Sarabharajudara#000006753"	"FRANCE                   "	36752	"Manufacturer#5           "	"vkoG26rE,dMq6n5 1tmQOW2wrU,xyXEahegZN,"	"16-508-617-7667"	"unusual instructions according to the blithely pending excuses are about the accounts. express,"
4582.50	"Sarabharajudara#000002513"	"ROMANIA                  "	64994	"Manufacturer#1           "	"nsHTqAc8vuw0sx0Z"	"29-819-858-5280"	" fluffily bold courts cajole furiously along the requests? carefully reg"
4582.50	"Sarabharajudara#000002513"	"ROMANIA                  "	64994	"Manufacturer#1           "	"nsHTqAc8vuw0sx0Z"	"29-819-858-5280"	" fluffily bold courts cajole furiously along the requests? carefully reg"
4559.02	"Sarabharajudara#000005834"	"UNITED KINGDOM           "	43329	"Manufacturer#2           "	"hrgnqRX qh"	"33-650-371-9232"	"l packages boost ironic, unusual accou"
4559.02	"Sarabharajudara#000005834"	"UNITED KINGDOM           "	43329	"Manufacturer#2           "	"hrgnqRX qh"	"33-650-371-9232"	"l packages boost ironic, unusual accou"
4552.61	"Sarabharajudara#000008938"	"GERMANY                  "	111404	"Manufacturer#2           "	"AymnssphwTHTJTy"	"17-363-294-6578"	"its hinder. final accounts integrate. furiou"
4552.61	"Sarabharajudara#000008938"	"GERMANY                  "	111404	"Manufacturer#2           "	"AymnssphwTHTJTy"	"17-363-294-6578"	"its hinder. final accounts integrate. furiou"
4518.31	"Sarabharajudara#000000149"	"FRANCE                   "	190148	"Manufacturer#5           "	"pVyWsjOidpHKp4NfKU4yLeym"	"16-660-553-2456"	"ts detect along the foxes. final Tiresias are. idly pending deposits haggle; even, blithe pin"
4518.31	"Sarabharajudara#000000149"	"FRANCE                   "	190148	"Manufacturer#5           "	"pVyWsjOidpHKp4NfKU4yLeym"	"16-660-553-2456"	"ts detect along the foxes. final Tiresias are. idly pending deposits haggle; even, blithe pin"
4480.50	"Sarabharajudara#000004200"	"GERMANY                  "	84199	"Manufacturer#1           "	"tCZuhXdCdu"	"17-277-324-6951"	"ss the furiously silent courts. quickly even foxes nod pe"
4480.50	"Sarabharajudara#000004200"	"GERMANY                  "	84199	"Manufacturer#1           "	"tCZuhXdCdu"	"17-277-324-6951"	"ss the furiously silent courts. quickly even foxes nod pe"
4383.12	"Sarabharajudara#000003023"	"RUSSIA                   "	157992	"Manufacturer#1           "	"a2vIsI7JLHFfBvJoSmPGfm"	"32-598-929-2593"	"arefully unusual instructions are slyly regular accounts. busy courts sleep furiously. "
4383.12	"Sarabharajudara#000003023"	"RUSSIA                   "	157992	"Manufacturer#1           "	"a2vIsI7JLHFfBvJoSmPGfm"	"32-598-929-2593"	"arefully unusual instructions are slyly regular accounts. busy courts sleep furiously. "
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	76602	"Manufacturer#4           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	76602	"Manufacturer#4           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	134077	"Manufacturer#4           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	134077	"Manufacturer#4           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	189098	"Manufacturer#1           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4373.08	"Sarabharajudara#000001617"	"FRANCE                   "	189098	"Manufacturer#1           "	"jnnhvsWAe9I5qanmlc"	"16-550-365-8843"	"s detect furiously about the bold, special foxes. blithely silent deposits na"
4353.56	"Sarabharajudara#000007823"	"RUSSIA                   "	27822	"Manufacturer#4           "	"i2 gFooiCz69Xb"	"32-905-204-8095"	"l theodolites use slyly accord"
4353.56	"Sarabharajudara#000007823"	"RUSSIA                   "	27822	"Manufacturer#4           "	"i2 gFooiCz69Xb"	"32-905-204-8095"	"l theodolites use slyly accord"
4332.54	"Sarabharajudara#000001751"	"UNITED KINGDOM           "	186714	"Manufacturer#2           "	"6jC4PcP6HCs9NMKN"	"33-309-349-1317"	"ular foxes haggle after the even platelets. furiously final accounts haggle slyly fluffily regula"
4332.54	"Sarabharajudara#000001751"	"UNITED KINGDOM           "	186714	"Manufacturer#2           "	"6jC4PcP6HCs9NMKN"	"33-309-349-1317"	"ular foxes haggle after the even platelets. furiously final accounts haggle slyly fluffily regula"
4331.41	"Sarabharajudara#000001494"	"GERMANY                  "	103963	"Manufacturer#5           "	"nqNP5GmByEQ496Y3MgUngQ"	"17-962-207-6063"	"fter the quickly even requests. blithely bold deposits haggle blithely. blithel"
4331.41	"Sarabharajudara#000001494"	"GERMANY                  "	103963	"Manufacturer#5           "	"nqNP5GmByEQ496Y3MgUngQ"	"17-962-207-6063"	"fter the quickly even requests. blithely bold deposits haggle blithely. blithel"
4324.51	"Sarabharajudara#000000957"	"UNITED KINGDOM           "	10956	"Manufacturer#5           "	"mSpFa,4jJ5R40k10YOvGEtl4KYjo"	"33-616-674-6155"	"hily after the fluffily regular dependencies. deposits nag regular, silent accounts. i"
4324.51	"Sarabharajudara#000000957"	"UNITED KINGDOM           "	10956	"Manufacturer#5           "	"mSpFa,4jJ5R40k10YOvGEtl4KYjo"	"33-616-674-6155"	"hily after the fluffily regular dependencies. deposits nag regular, silent accounts. i"
4305.85	"Sarabharajudara#000007241"	"GERMANY                  "	12238	"Manufacturer#1           "	"8xtX4J2 GxQ,4"	"17-604-128-7288"	"ke carefully across the even, pending asymptotes. busily even foxes wake slyly i"
4305.85	"Sarabharajudara#000007241"	"GERMANY                  "	12238	"Manufacturer#1           "	"8xtX4J2 GxQ,4"	"17-604-128-7288"	"ke carefully across the even, pending asymptotes. busily even foxes wake slyly i"
4241.79	"Sarabharajudara#000005610"	"RUSSIA                   "	55609	"Manufacturer#3           "	"0hB1oH1SCbnuqzgH8pY3lsPjK HVLY3qa6UGWY"	"32-442-482-1719"	"gular dependencies use carefully fluffily final packages. fluffily final deposits impress slyly"
4241.79	"Sarabharajudara#000005610"	"RUSSIA                   "	55609	"Manufacturer#3           "	"0hB1oH1SCbnuqzgH8pY3lsPjK HVLY3qa6UGWY"	"32-442-482-1719"	"gular dependencies use carefully fluffily final packages. fluffily final deposits impress slyly"
4232.40	"Sarabharajudara#000002759"	"ROMANIA                  "	75237	"Manufacturer#4           "	"UMMOYgG lDV2niUiXUx4Ft1SzT6ix6Vy7qej4sO"	"29-818-946-1920"	"gle quickly furiously express requests. slyly regular ideas haggle. requests sleep. slyly p"
4232.40	"Sarabharajudara#000002759"	"ROMANIA                  "	75237	"Manufacturer#4           "	"UMMOYgG lDV2niUiXUx4Ft1SzT6ix6Vy7qej4sO"	"29-818-946-1920"	"gle quickly furiously express requests. slyly regular ideas haggle. requests sleep. slyly p"
4232.40	"Sarabharajudara#000002759"	"ROMANIA                  "	140244	"Manufacturer#4           "	"UMMOYgG lDV2niUiXUx4Ft1SzT6ix6Vy7qej4sO"	"29-818-946-1920"	"gle quickly furiously express requests. slyly regular ideas haggle. requests sleep. slyly p"
4232.40	"Sarabharajudara#000002759"	"ROMANIA                  "	140244	"Manufacturer#4           "	"UMMOYgG lDV2niUiXUx4Ft1SzT6ix6Vy7qej4sO"	"29-818-946-1920"	"gle quickly furiously express requests. slyly regular ideas haggle. requests sleep. slyly p"
4162.42	"Sarabharajudara#000002723"	"UNITED KINGDOM           "	70215	"Manufacturer#3           "	",M8ShKTXyBramz 90ahZXSFpbF16a2JYqPDv"	"33-174-542-2072"	"ress foxes detect along the express packages. accounts sleep blithely alongside of"
4162.42	"Sarabharajudara#000002723"	"UNITED KINGDOM           "	70215	"Manufacturer#3           "	",M8ShKTXyBramz 90ahZXSFpbF16a2JYqPDv"	"33-174-542-2072"	"ress foxes detect along the express packages. accounts sleep blithely alongside of"
4102.78	"Sarabharajudara#000003356"	"FRANCE                   "	100845	"Manufacturer#1           "	"jtlug57,ke9cq9ECwEXA1EKTp"	"16-135-705-4908"	"counts are slyly regular deposits. blithely regular acco"
4102.78	"Sarabharajudara#000003356"	"FRANCE                   "	100845	"Manufacturer#1           "	"jtlug57,ke9cq9ECwEXA1EKTp"	"16-135-705-4908"	"counts are slyly regular deposits. blithely regular acco"
4102.46	"Sarabharajudara#000004597"	"FRANCE                   "	192077	"Manufacturer#1           "	"gKuHIUE7XWqK9ZDCA,Kp0jFza4PvTq,RtFF"	"16-130-150-6625"	" packages cajole. regular packages wak"
4102.46	"Sarabharajudara#000004597"	"FRANCE                   "	192077	"Manufacturer#1           "	"gKuHIUE7XWqK9ZDCA,Kp0jFza4PvTq,RtFF"	"16-130-150-6625"	" packages cajole. regular packages wak"
4045.69	"Sarabharajudara#000004475"	"ROMANIA                  "	41970	"Manufacturer#3           "	"fCyPeYGEI7pEhuAPIbHMml"	"29-223-770-7780"	"the slyly even accounts. close"
4045.69	"Sarabharajudara#000004475"	"ROMANIA                  "	41970	"Manufacturer#3           "	"fCyPeYGEI7pEhuAPIbHMml"	"29-223-770-7780"	"the slyly even accounts. close"
3996.68	"Sarabharajudara#000001384"	"FRANCE                   "	106363	"Manufacturer#2           "	"fjgJwG4DViJrxMxJbO2kS2"	"16-195-562-6135"	"ages. ironic, ironic packages after the carefully even re"
3996.68	"Sarabharajudara#000001384"	"FRANCE                   "	106363	"Manufacturer#2           "	"fjgJwG4DViJrxMxJbO2kS2"	"16-195-562-6135"	"ages. ironic, ironic packages after the carefully even re"
3996.68	"Sarabharajudara#000001384"	"FRANCE                   "	138870	"Manufacturer#1           "	"fjgJwG4DViJrxMxJbO2kS2"	"16-195-562-6135"	"ages. ironic, ironic packages after the carefully even re"
3996.68	"Sarabharajudara#000001384"	"FRANCE                   "	138870	"Manufacturer#1           "	"fjgJwG4DViJrxMxJbO2kS2"	"16-195-562-6135"	"ages. ironic, ironic packages after the carefully even re"
3976.59	"Sarabharajudara#000005024"	"ROMANIA                  "	10021	"Manufacturer#5           "	"y0,QhJZwQSjhRC6 rPsa5tLcmjRy8LKjuS"	"29-535-675-8153"	"y ironic deposits wake blithely above the unusual courts. "
3976.59	"Sarabharajudara#000005024"	"ROMANIA                  "	10021	"Manufacturer#5           "	"y0,QhJZwQSjhRC6 rPsa5tLcmjRy8LKjuS"	"29-535-675-8153"	"y ironic deposits wake blithely above the unusual courts. "
3905.57	"Sarabharajudara#000008692"	"FRANCE                   "	46187	"Manufacturer#4           "	"ke4YY0yawKS8 ICpJfIJt0tXGymxAgt"	"16-592-792-3475"	" express theodolites snooze blithely final requests. fluffily final deposits alo"
3905.57	"Sarabharajudara#000008692"	"FRANCE                   "	46187	"Manufacturer#4           "	"ke4YY0yawKS8 ICpJfIJt0tXGymxAgt"	"16-592-792-3475"	" express theodolites snooze blithely final requests. fluffily final deposits alo"
3905.57	"Sarabharajudara#000008692"	"FRANCE                   "	63679	"Manufacturer#5           "	"ke4YY0yawKS8 ICpJfIJt0tXGymxAgt"	"16-592-792-3475"	" express theodolites snooze blithely final requests. fluffily final deposits alo"
3905.57	"Sarabharajudara#000008692"	"FRANCE                   "	63679	"Manufacturer#5           "	"ke4YY0yawKS8 ICpJfIJt0tXGymxAgt"	"16-592-792-3475"	" express theodolites snooze blithely final requests. fluffily final deposits alo"
3859.72	"Sarabharajudara#000003255"	"RUSSIA                   "	28250	"Manufacturer#5           "	"4TB2q kbKyVY3"	"32-693-382-9279"	"nstructions along the carefully final deposits doubt qui"
3859.72	"Sarabharajudara#000003255"	"RUSSIA                   "	28250	"Manufacturer#5           "	"4TB2q kbKyVY3"	"32-693-382-9279"	"nstructions along the carefully final deposits doubt qui"
3855.74	"Sarabharajudara#000000815"	"GERMANY                  "	38311	"Manufacturer#3           "	"3f8XIvP m9v5fv"	"17-984-775-9865"	"ms. final packages use finall"
3855.74	"Sarabharajudara#000000815"	"GERMANY                  "	38311	"Manufacturer#3           "	"3f8XIvP m9v5fv"	"17-984-775-9865"	"ms. final packages use finall"
3820.39	"Sarabharajudara#000004746"	"FRANCE                   "	17242	"Manufacturer#4           "	"HrNlq N3KfDAfcfX3uho4LqI"	"16-545-107-4292"	" the slyly regular ideas. regular ideas slee"
3820.39	"Sarabharajudara#000004746"	"FRANCE                   "	17242	"Manufacturer#4           "	"HrNlq N3KfDAfcfX3uho4LqI"	"16-545-107-4292"	" the slyly regular ideas. regular ideas slee"
3810.81	"Sarabharajudara#000000684"	"ROMANIA                  "	148169	"Manufacturer#4           "	"nqw,GGxCoNZ3UOuIa0edX3SdoYKER"	"29-345-334-1955"	"sts are slyly. doggedly final warhorses wake carefully after the deposits. reg"
3810.81	"Sarabharajudara#000000684"	"ROMANIA                  "	148169	"Manufacturer#4           "	"nqw,GGxCoNZ3UOuIa0edX3SdoYKER"	"29-345-334-1955"	"sts are slyly. doggedly final warhorses wake carefully after the deposits. reg"
3784.36	"Sarabharajudara#000003082"	"UNITED KINGDOM           "	85557	"Manufacturer#1           "	"vLhIfPUhiW1Y rYmcj"	"33-680-262-1683"	"y after the unusual asymptot"
3784.36	"Sarabharajudara#000003082"	"UNITED KINGDOM           "	85557	"Manufacturer#1           "	"vLhIfPUhiW1Y rYmcj"	"33-680-262-1683"	"y after the unusual asymptot"
3778.48	"Sarabharajudara#000002397"	"FRANCE                   "	39893	"Manufacturer#2           "	"E0b,zxlk yKgtoKg1jH,"	"16-439-996-6973"	"bold pinto beans haggle slyly. silent, ironic requests"
3778.48	"Sarabharajudara#000002397"	"FRANCE                   "	39893	"Manufacturer#2           "	"E0b,zxlk yKgtoKg1jH,"	"16-439-996-6973"	"bold pinto beans haggle slyly. silent, ironic requests"
3778.48	"Sarabharajudara#000002397"	"FRANCE                   "	134857	"Manufacturer#5           "	"E0b,zxlk yKgtoKg1jH,"	"16-439-996-6973"	"bold pinto beans haggle slyly. silent, ironic requests"
3778.48	"Sarabharajudara#000002397"	"FRANCE                   "	134857	"Manufacturer#5           "	"E0b,zxlk yKgtoKg1jH,"	"16-439-996-6973"	"bold pinto beans haggle slyly. silent, ironic requests"
3761.10	"Sarabharajudara#000003596"	"GERMANY                  "	176044	"Manufacturer#2           "	"pyXt0UgE4TvoiL"	"17-179-432-8934"	"ven requests. carefully regular deposits are blithely furiously final requests. spe"
3761.10	"Sarabharajudara#000003596"	"GERMANY                  "	176044	"Manufacturer#2           "	"pyXt0UgE4TvoiL"	"17-179-432-8934"	"ven requests. carefully regular deposits are blithely furiously final requests. spe"
3758.64	"Sarabharajudara#000000247"	"UNITED KINGDOM           "	102716	"Manufacturer#5           "	"0bkES oiL2joJGmxdGwPfVCOL,pIQ4JNZBPnOR"	"33-695-935-2388"	"final requests. final accounts affix. express accounts about the furio"
3758.64	"Sarabharajudara#000000247"	"UNITED KINGDOM           "	102716	"Manufacturer#5           "	"0bkES oiL2joJGmxdGwPfVCOL,pIQ4JNZBPnOR"	"33-695-935-2388"	"final requests. final accounts affix. express accounts about the furio"
3758.64	"Sarabharajudara#000000247"	"UNITED KINGDOM           "	160246	"Manufacturer#2           "	"0bkES oiL2joJGmxdGwPfVCOL,pIQ4JNZBPnOR"	"33-695-935-2388"	"final requests. final accounts affix. express accounts about the furio"
3758.64	"Sarabharajudara#000000247"	"UNITED KINGDOM           "	160246	"Manufacturer#2           "	"0bkES oiL2joJGmxdGwPfVCOL,pIQ4JNZBPnOR"	"33-695-935-2388"	"final requests. final accounts affix. express accounts about the furio"
3730.29	"Sarabharajudara#000004785"	"GERMANY                  "	89768	"Manufacturer#2           "	"zKnM6Wq5if1ovdmAloFLN48t9 RtO,zCz  "	"17-977-283-2115"	"quickly pending platelets. regular, unusual foxes affix carefully after the packages. final "
3730.29	"Sarabharajudara#000004785"	"GERMANY                  "	89768	"Manufacturer#2           "	"zKnM6Wq5if1ovdmAloFLN48t9 RtO,zCz  "	"17-977-283-2115"	"quickly pending platelets. regular, unusual foxes affix carefully after the packages. final "
3711.33	"Sarabharajudara#000007240"	"UNITED KINGDOM           "	144725	"Manufacturer#2           "	"ApzTXaYhoCBqijpuu29od3cEIhAsr"	"33-140-585-2550"	"uests-- blithely blithe theodolites wake. regular excuses"
3711.33	"Sarabharajudara#000007240"	"UNITED KINGDOM           "	144725	"Manufacturer#2           "	"ApzTXaYhoCBqijpuu29od3cEIhAsr"	"33-140-585-2550"	"uests-- blithely blithe theodolites wake. regular excuses"
3689.03	"Sarabharajudara#000001419"	"RUSSIA                   "	146390	"Manufacturer#4           "	"9wbge8NxXVd5LbIlNA,DjR0sjasMyxC7oANgSQw"	"32-865-313-5333"	"uld have to affix quickly after th"
3689.03	"Sarabharajudara#000001419"	"RUSSIA                   "	146390	"Manufacturer#4           "	"9wbge8NxXVd5LbIlNA,DjR0sjasMyxC7oANgSQw"	"32-865-313-5333"	"uld have to affix quickly after th"
3681.43	"Sarabharajudara#000001604"	"FRANCE                   "	164055	"Manufacturer#1           "	"JQqqQ1FeZHi2UV9Ji2o8WW,1w4ZdYHoA v0m,g"	"16-709-747-9026"	"le quickly: unusual, bold requests about the ironic excuses"
3681.43	"Sarabharajudara#000001604"	"FRANCE                   "	164055	"Manufacturer#1           "	"JQqqQ1FeZHi2UV9Ji2o8WW,1w4ZdYHoA v0m,g"	"16-709-747-9026"	"le quickly: unusual, bold requests about the ironic excuses"
3605.55	"Sarabharajudara#000006237"	"FRANCE                   "	91218	"Manufacturer#4           "	"ghp4,RZ08rhbRUlI352a"	"16-655-635-6500"	"accounts are slyly unusual, regular deposits. even as"
3605.55	"Sarabharajudara#000006237"	"FRANCE                   "	91218	"Manufacturer#4           "	"ghp4,RZ08rhbRUlI352a"	"16-655-635-6500"	"accounts are slyly unusual, regular deposits. even as"
3573.92	"Sarabharajudara#000008316"	"ROMANIA                  "	173281	"Manufacturer#3           "	"M,BrvLmLtbbDy5O"	"29-143-826-7135"	"counts must have to nag across the carefully unusua"
3573.92	"Sarabharajudara#000008316"	"ROMANIA                  "	173281	"Manufacturer#3           "	"M,BrvLmLtbbDy5O"	"29-143-826-7135"	"counts must have to nag across the carefully unusua"
3563.05	"Sarabharajudara#000007887"	"ROMANIA                  "	47886	"Manufacturer#1           "	"Ee40AjRtmPosrTS,hTJ3tTRYbDpvnxfl"	"29-222-572-2267"	"sits haggle slyly ironic, final somas. furiously special de"
3563.05	"Sarabharajudara#000007887"	"ROMANIA                  "	47886	"Manufacturer#1           "	"Ee40AjRtmPosrTS,hTJ3tTRYbDpvnxfl"	"29-222-572-2267"	"sits haggle slyly ironic, final somas. furiously special de"
3558.18	"Sarabharajudara#000002672"	"GERMANY                  "	97653	"Manufacturer#3           "	"ltw3PjtQ05 KumuVhrzxUnVgueMkhG1E8Ai8A70"	"17-545-775-1990"	"le carefully. carefully pending reque"
3558.18	"Sarabharajudara#000002672"	"GERMANY                  "	97653	"Manufacturer#3           "	"ltw3PjtQ05 KumuVhrzxUnVgueMkhG1E8Ai8A70"	"17-545-775-1990"	"le carefully. carefully pending reque"
3556.47	"Sarabharajudara#000000032"	"UNITED KINGDOM           "	52516	"Manufacturer#5           "	"yvoD3TtZSx1skQNCK8agk5bZlZLug"	"33-484-637-7873"	"usly even depths. quickly ironic theodolites s"
3556.47	"Sarabharajudara#000000032"	"UNITED KINGDOM           "	52516	"Manufacturer#5           "	"yvoD3TtZSx1skQNCK8agk5bZlZLug"	"33-484-637-7873"	"usly even depths. quickly ironic theodolites s"
3555.22	"Sarabharajudara#000002358"	"RUSSIA                   "	169841	"Manufacturer#3           "	"4ucUvhCCU MESh"	"32-973-594-8385"	"lent instructions cajole fluffily among the requests. fluffily ironic asymptotes nag fluffily"
3555.22	"Sarabharajudara#000002358"	"RUSSIA                   "	169841	"Manufacturer#3           "	"4ucUvhCCU MESh"	"32-973-594-8385"	"lent instructions cajole fluffily among the requests. fluffily ironic asymptotes nag fluffily"
3550.25	"Sarabharajudara#000004839"	"UNITED KINGDOM           "	177287	"Manufacturer#3           "	"JxtU4NY,TdGJSAOt1,du4ujxFo0W,faXtwrWnt"	"33-450-585-1565"	"oxes. regular ideas are carefully furiously ironic requests: blithely special deposits across t"
3550.25	"Sarabharajudara#000004839"	"UNITED KINGDOM           "	177287	"Manufacturer#3           "	"JxtU4NY,TdGJSAOt1,du4ujxFo0W,faXtwrWnt"	"33-450-585-1565"	"oxes. regular ideas are carefully furiously ironic requests: blithely special deposits across t"
3540.29	"Sarabharajudara#000008797"	"RUSSIA                   "	193758	"Manufacturer#4           "	"dyz8WERDG3fdz"	"32-474-915-2675"	". theodolites boost. regular requests play? blithely special dolphins cajole unusual asympto"
3540.29	"Sarabharajudara#000008797"	"RUSSIA                   "	193758	"Manufacturer#4           "	"dyz8WERDG3fdz"	"32-474-915-2675"	". theodolites boost. regular requests play? blithely special dolphins cajole unusual asympto"
3538.07	"Sarabharajudara#000009232"	"RUSSIA                   "	189231	"Manufacturer#5           "	"oKg,qpT55rwxqbmq1gyf7HttG9"	"32-770-768-2763"	"ructions cajole blithely. unusual, regular ac"
3538.07	"Sarabharajudara#000009232"	"RUSSIA                   "	189231	"Manufacturer#5           "	"oKg,qpT55rwxqbmq1gyf7HttG9"	"32-770-768-2763"	"ructions cajole blithely. unusual, regular ac"
3530.31	"Sarabharajudara#000003534"	"GERMANY                  "	58523	"Manufacturer#5           "	"vGLHyvqDzoGJ,9QF4S"	"17-420-181-2025"	"ndencies cajole quickly. special dinos cajole bold theodolites. pending depo"
3530.31	"Sarabharajudara#000003534"	"GERMANY                  "	58523	"Manufacturer#5           "	"vGLHyvqDzoGJ,9QF4S"	"17-420-181-2025"	"ndencies cajole quickly. special dinos cajole bold theodolites. pending depo"
3498.30	"Sarabharajudara#000002542"	"RUSSIA                   "	77527	"Manufacturer#5           "	"vPQq7x1BGpdKke797PC2 eYAAMpVMi"	"32-760-854-8942"	" haggle blithely slyly special "
3498.30	"Sarabharajudara#000002542"	"RUSSIA                   "	77527	"Manufacturer#5           "	"vPQq7x1BGpdKke797PC2 eYAAMpVMi"	"32-760-854-8942"	" haggle blithely slyly special "
3429.30	"Sarabharajudara#000003963"	"GERMANY                  "	186408	"Manufacturer#1           "	"r8VL5GKQMJTx"	"17-350-945-1631"	"posits. accounts after the quickly "
3429.30	"Sarabharajudara#000003963"	"GERMANY                  "	186408	"Manufacturer#1           "	"r8VL5GKQMJTx"	"17-350-945-1631"	"posits. accounts after the quickly "
3341.97	"Sarabharajudara#000001239"	"FRANCE                   "	48734	"Manufacturer#3           "	"w7zZA8K5TcHMmFtojh3uGVOPHTaPIwE"	"16-805-237-6265"	"e furiously regular foxes boost blithely against the regular dep"
3341.97	"Sarabharajudara#000001239"	"FRANCE                   "	48734	"Manufacturer#3           "	"w7zZA8K5TcHMmFtojh3uGVOPHTaPIwE"	"16-805-237-6265"	"e furiously regular foxes boost blithely against the regular dep"
3316.16	"Sarabharajudara#000001002"	"RUSSIA                   "	158486	"Manufacturer#2           "	"bzwzvRnMTA2IEIv,AKydTru0vsbETQkhV"	"32-102-374-6308"	"ns are carefully. blithely regular requests cajole furiously. furiously "
3316.16	"Sarabharajudara#000001002"	"RUSSIA                   "	158486	"Manufacturer#2           "	"bzwzvRnMTA2IEIv,AKydTru0vsbETQkhV"	"32-102-374-6308"	"ns are carefully. blithely regular requests cajole furiously. furiously "
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	21063	"Manufacturer#3           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	21063	"Manufacturer#3           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	98540	"Manufacturer#1           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	98540	"Manufacturer#1           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	178516	"Manufacturer#3           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3244.81	"Sarabharajudara#000006068"	"RUSSIA                   "	178516	"Manufacturer#3           "	"bToNEQv4zKzQ1NypZj00YjzYhrm94W2,sOYruF0"	"32-155-311-9768"	"nal accounts. silent forges against"
3240.41	"Sarabharajudara#000004164"	"FRANCE                   "	159133	"Manufacturer#3           "	"f60HY65zdJb6eSCUYOmm"	"16-161-750-6814"	"y pending requests. furiously fin"
3240.41	"Sarabharajudara#000004164"	"FRANCE                   "	159133	"Manufacturer#3           "	"f60HY65zdJb6eSCUYOmm"	"16-161-750-6814"	"y pending requests. furiously fin"
3224.71	"Sarabharajudara#000003037"	"RUSSIA                   "	8036	"Manufacturer#4           "	"aBPbT4XfxDheA"	"32-150-300-6644"	"pending dependencies. carefully silent deposits hang slyly brave platelets! pac"
3224.71	"Sarabharajudara#000003037"	"RUSSIA                   "	8036	"Manufacturer#4           "	"aBPbT4XfxDheA"	"32-150-300-6644"	"pending dependencies. carefully silent deposits hang slyly brave platelets! pac"
3220.82	"Sarabharajudara#000008360"	"UNITED KINGDOM           "	78359	"Manufacturer#4           "	"jeLcK7YUbZzQuwD9a,1F"	"33-764-209-1683"	"regular grouches engage slyly unusual foxes. slyly pending packages kindle carefully acr"
3220.82	"Sarabharajudara#000008360"	"UNITED KINGDOM           "	78359	"Manufacturer#4           "	"jeLcK7YUbZzQuwD9a,1F"	"33-764-209-1683"	"regular grouches engage slyly unusual foxes. slyly pending packages kindle carefully acr"
3219.06	"Sarabharajudara#000001808"	"FRANCE                   "	81807	"Manufacturer#5           "	"5BpK38HqFkGcR6fB8R2fJ"	"16-705-363-3885"	"out the quickly regular requests cajole ironic, regular deposits. bli"
3219.06	"Sarabharajudara#000001808"	"FRANCE                   "	81807	"Manufacturer#5           "	"5BpK38HqFkGcR6fB8R2fJ"	"16-705-363-3885"	"out the quickly regular requests cajole ironic, regular deposits. bli"
3210.50	"Sarabharajudara#000001666"	"RUSSIA                   "	106645	"Manufacturer#1           "	"z4t8jiCjahT7K E8l"	"32-154-546-8208"	"bove the deposits wake blithely above the eve"
3210.50	"Sarabharajudara#000001666"	"RUSSIA                   "	106645	"Manufacturer#1           "	"z4t8jiCjahT7K E8l"	"32-154-546-8208"	"bove the deposits wake blithely above the eve"
3197.65	"Sarabharajudara#000009225"	"RUSSIA                   "	139224	"Manufacturer#4           "	"s,MIHdC7zF"	"32-542-446-4004"	"he carefully regular packages. fluffily pending deposits integrate. carefully pendin"
3197.65	"Sarabharajudara#000009225"	"RUSSIA                   "	139224	"Manufacturer#4           "	"s,MIHdC7zF"	"32-542-446-4004"	"he carefully regular packages. fluffily pending deposits integrate. carefully pendin"
3153.90	"Sarabharajudara#000007145"	"RUSSIA                   "	197144	"Manufacturer#1           "	"eG9ZPCfNuIuxusKl"	"32-331-188-7406"	"counts play. fluffily pending accounts are. ruthless,"
3153.90	"Sarabharajudara#000007145"	"RUSSIA                   "	197144	"Manufacturer#1           "	"eG9ZPCfNuIuxusKl"	"32-331-188-7406"	"counts play. fluffily pending accounts are. ruthless,"
3145.86	"Sarabharajudara#000001108"	"GERMANY                  "	8607	"Manufacturer#5           "	"9cIxntXdykwaYWA2"	"17-726-989-5062"	"g to the pending requests. silent asymptotes boost blithely. quietly iron"
3145.86	"Sarabharajudara#000001108"	"GERMANY                  "	8607	"Manufacturer#5           "	"9cIxntXdykwaYWA2"	"17-726-989-5062"	"g to the pending requests. silent asymptotes boost blithely. quietly iron"
3145.86	"Sarabharajudara#000001108"	"GERMANY                  "	171107	"Manufacturer#3           "	"9cIxntXdykwaYWA2"	"17-726-989-5062"	"g to the pending requests. silent asymptotes boost blithely. quietly iron"
3145.86	"Sarabharajudara#000001108"	"GERMANY                  "	171107	"Manufacturer#3           "	"9cIxntXdykwaYWA2"	"17-726-989-5062"	"g to the pending requests. silent asymptotes boost blithely. quietly iron"
3115.27	"Sarabharajudara#000001227"	"UNITED KINGDOM           "	106206	"Manufacturer#1           "	"cXdKu5KSQ1yaF,EiRLpcP"	"33-515-927-3294"	"ithely even packages cajole slyly. slyly"
3115.27	"Sarabharajudara#000001227"	"UNITED KINGDOM           "	106206	"Manufacturer#1           "	"cXdKu5KSQ1yaF,EiRLpcP"	"33-515-927-3294"	"ithely even packages cajole slyly. slyly"
3070.27	"Sarabharajudara#000009346"	"FRANCE                   "	111812	"Manufacturer#5           "	"F2,WuMvhDqdLGa6ZGWCvn mGK"	"16-674-943-9382"	"ress theodolites are. furiously pending pinto b"
3070.27	"Sarabharajudara#000009346"	"FRANCE                   "	111812	"Manufacturer#5           "	"F2,WuMvhDqdLGa6ZGWCvn mGK"	"16-674-943-9382"	"ress theodolites are. furiously pending pinto b"
3011.28	"Sarabharajudara#000003026"	"ROMANIA                  "	35516	"Manufacturer#4           "	"La4dO0Ey1H2mXK8 N"	"29-673-539-2157"	"usly unusual deposits. car"
3011.28	"Sarabharajudara#000003026"	"ROMANIA                  "	35516	"Manufacturer#4           "	"La4dO0Ey1H2mXK8 N"	"29-673-539-2157"	"usly unusual deposits. car"
2962.92	"Sarabharajudara#000004476"	"ROMANIA                  "	26969	"Manufacturer#3           "	"QYhizpJ2Hlsgz,waBJ3hvDy1FP"	"29-423-720-3024"	"usual platelets. furiously fina"
2962.92	"Sarabharajudara#000004476"	"ROMANIA                  "	26969	"Manufacturer#3           "	"QYhizpJ2Hlsgz,waBJ3hvDy1FP"	"29-423-720-3024"	"usual platelets. furiously fina"
2938.97	"Sarabharajudara#000002124"	"RUSSIA                   "	22123	"Manufacturer#5           "	"mT2TCWCpXJFg0ISAPlvbQPwrj Gd"	"32-731-692-4007"	"platelets. fluffily pending deposits boost. carefully even request"
2938.97	"Sarabharajudara#000002124"	"RUSSIA                   "	22123	"Manufacturer#5           "	"mT2TCWCpXJFg0ISAPlvbQPwrj Gd"	"32-731-692-4007"	"platelets. fluffily pending deposits boost. carefully even request"
2920.34	"Sarabharajudara#000004897"	"GERMANY                  "	197339	"Manufacturer#2           "	"h,nzVUV Lvj9yKdb"	"17-738-542-1481"	"accounts. blithely special Tiresias cajole blithely above the bl"
2920.34	"Sarabharajudara#000004897"	"GERMANY                  "	197339	"Manufacturer#2           "	"h,nzVUV Lvj9yKdb"	"17-738-542-1481"	"accounts. blithely special Tiresias cajole blithely above the bl"
2905.10	"Sarabharajudara#000002055"	"RUSSIA                   "	49550	"Manufacturer#1           "	"h14IqRaCVKW"	"32-368-197-3979"	"ly fluffy theodolites boost "
2905.10	"Sarabharajudara#000002055"	"RUSSIA                   "	49550	"Manufacturer#1           "	"h14IqRaCVKW"	"32-368-197-3979"	"ly fluffy theodolites boost "
2887.89	"Sarabharajudara#000002623"	"UNITED KINGDOM           "	125086	"Manufacturer#3           "	" 4Fu1G9iVp4ID"	"33-479-498-3860"	"ly. blithely final requests integra"
2887.89	"Sarabharajudara#000002623"	"UNITED KINGDOM           "	125086	"Manufacturer#3           "	" 4Fu1G9iVp4ID"	"33-479-498-3860"	"ly. blithely final requests integra"
2887.89	"Sarabharajudara#000002623"	"UNITED KINGDOM           "	195065	"Manufacturer#3           "	" 4Fu1G9iVp4ID"	"33-479-498-3860"	"ly. blithely final requests integra"
2887.89	"Sarabharajudara#000002623"	"UNITED KINGDOM           "	195065	"Manufacturer#3           "	" 4Fu1G9iVp4ID"	"33-479-498-3860"	"ly. blithely final requests integra"
2886.07	"Sarabharajudara#000005217"	"UNITED KINGDOM           "	27710	"Manufacturer#5           "	"XKWuIicCsmrN6TOiPwZiC60suCz4vb2GxAcLLEIi"	"33-238-443-5421"	"ly warthogs. regular braids sleep above the fluffily even tithes! fluffily unusual acco"
2886.07	"Sarabharajudara#000005217"	"UNITED KINGDOM           "	27710	"Manufacturer#5           "	"XKWuIicCsmrN6TOiPwZiC60suCz4vb2GxAcLLEIi"	"33-238-443-5421"	"ly warthogs. regular braids sleep above the fluffily even tithes! fluffily unusual acco"
2881.79	"Sarabharajudara#000009628"	"ROMANIA                  "	189627	"Manufacturer#5           "	"W42Aqclp4Ov "	"29-745-342-4598"	"ccounts haggle furiously bold packages. slyly even theodolites a"
2881.79	"Sarabharajudara#000009628"	"ROMANIA                  "	189627	"Manufacturer#5           "	"W42Aqclp4Ov "	"29-745-342-4598"	"ccounts haggle furiously bold packages. slyly even theodolites a"
2876.63	"Sarabharajudara#000009272"	"FRANCE                   "	89271	"Manufacturer#2           "	"VFcTkTcm7NEEenCtro85Bwd7syhEHEZ9Va"	"16-648-900-1004"	"thely bold excuses integrate always even dependencies. carefully express "
2876.63	"Sarabharajudara#000009272"	"FRANCE                   "	89271	"Manufacturer#2           "	"VFcTkTcm7NEEenCtro85Bwd7syhEHEZ9Va"	"16-648-900-1004"	"thely bold excuses integrate always even dependencies. carefully express "
2848.81	"Sarabharajudara#000003564"	"FRANCE                   "	3563	"Manufacturer#1           "	"tYOfapsdmZRAq VMX73Mc9BsGa"	"16-720-599-1105"	" packages haggle after the silent de"
2848.81	"Sarabharajudara#000003564"	"FRANCE                   "	3563	"Manufacturer#1           "	"tYOfapsdmZRAq VMX73Mc9BsGa"	"16-720-599-1105"	" packages haggle after the silent de"
2834.61	"Sarabharajudara#000003907"	"ROMANIA                  "	41402	"Manufacturer#3           "	"cN6jbd1 q6v3PDE"	"29-335-916-5312"	"uffily unusual deposits. even packages haggle carefully regular dependencies: fluffily express pint"
2834.61	"Sarabharajudara#000003907"	"ROMANIA                  "	41402	"Manufacturer#3           "	"cN6jbd1 q6v3PDE"	"29-335-916-5312"	"uffily unusual deposits. even packages haggle carefully regular dependencies: fluffily express pint"
2808.75	"Sarabharajudara#000001323"	"GERMANY                  "	3822	"Manufacturer#5           "	"PAh52FWueSB04tXU"	"17-522-987-4040"	"tes will have to boost above the carefully final t"
2808.75	"Sarabharajudara#000001323"	"GERMANY                  "	3822	"Manufacturer#5           "	"PAh52FWueSB04tXU"	"17-522-987-4040"	"tes will have to boost above the carefully final t"
2781.49	"Sarabharajudara#000008949"	"UNITED KINGDOM           "	141406	"Manufacturer#1           "	"bnFmDdpFen,dYubmHvuJuxQkaSr OANifA9Q"	"33-510-996-1338"	" cajole blithely alongside of the regularly final packages; slyly "
2781.49	"Sarabharajudara#000008949"	"UNITED KINGDOM           "	141406	"Manufacturer#1           "	"bnFmDdpFen,dYubmHvuJuxQkaSr OANifA9Q"	"33-510-996-1338"	" cajole blithely alongside of the regularly final packages; slyly "
2761.59	"Sarabharajudara#000000839"	"FRANCE                   "	188320	"Manufacturer#5           "	"1fSx9Sv6LraqnVP3u"	"16-845-687-7291"	"ess, regular accounts haggle slyly across the carefully "
2761.59	"Sarabharajudara#000000839"	"FRANCE                   "	188320	"Manufacturer#5           "	"1fSx9Sv6LraqnVP3u"	"16-845-687-7291"	"ess, regular accounts haggle slyly across the carefully "
2754.66	"Sarabharajudara#000003478"	"RUSSIA                   "	30974	"Manufacturer#5           "	"mRuc7TmfUuV4YK93HhggTA4lyhoQDbEEO"	"32-511-233-7238"	" ironic accounts according to the blithel"
2754.66	"Sarabharajudara#000003478"	"RUSSIA                   "	30974	"Manufacturer#5           "	"mRuc7TmfUuV4YK93HhggTA4lyhoQDbEEO"	"32-511-233-7238"	" ironic accounts according to the blithel"
2753.77	"Sarabharajudara#000000180"	"GERMANY                  "	100179	"Manufacturer#3           "	"JJzFp5wZcS0KpMLM95tYmq5Pv526UBfT8vrfwBk"	"17-600-237-1665"	"ic deposits wake furiously even, express accounts. slyly express packages detect doggedly"
2753.77	"Sarabharajudara#000000180"	"GERMANY                  "	100179	"Manufacturer#3           "	"JJzFp5wZcS0KpMLM95tYmq5Pv526UBfT8vrfwBk"	"17-600-237-1665"	"ic deposits wake furiously even, express accounts. slyly express packages detect doggedly"
2672.84	"Sarabharajudara#000008676"	"UNITED KINGDOM           "	121139	"Manufacturer#3           "	",Ch0bG pkQ0,F70Ei2Euz8HoF,NSIUwMInY"	"33-230-218-4163"	" the daring ideas. bold theodolites along the sometimes bold pinto bea"
2672.84	"Sarabharajudara#000008676"	"UNITED KINGDOM           "	121139	"Manufacturer#3           "	",Ch0bG pkQ0,F70Ei2Euz8HoF,NSIUwMInY"	"33-230-218-4163"	" the daring ideas. bold theodolites along the sometimes bold pinto bea"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	47760	"Manufacturer#2           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	47760	"Manufacturer#2           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	150264	"Manufacturer#4           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	150264	"Manufacturer#4           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	152719	"Manufacturer#2           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2638.54	"Sarabharajudara#000000265"	"ROMANIA                  "	152719	"Manufacturer#2           "	"eHF4Edu,B8,NgBSSEV4xNC37i1q08WCNKyOe6jP"	"29-734-865-6334"	"le evenly besides the fluffily fina"
2626.90	"Sarabharajudara#000009158"	"RUSSIA                   "	171606	"Manufacturer#4           "	"it9tAeDAu9o1xG,G1JH"	"32-604-740-5833"	"s the silent pinto beans haggle unusual,"
2626.90	"Sarabharajudara#000009158"	"RUSSIA                   "	171606	"Manufacturer#4           "	"it9tAeDAu9o1xG,G1JH"	"32-604-740-5833"	"s the silent pinto beans haggle unusual,"
2585.33	"Sarabharajudara#000007257"	"UNITED KINGDOM           "	109726	"Manufacturer#5           "	"ag76lMmwqT"	"33-820-388-8545"	" express, final pinto beans. ironic, final requests sleep. furiously final ideas acros"
2585.33	"Sarabharajudara#000007257"	"UNITED KINGDOM           "	109726	"Manufacturer#5           "	"ag76lMmwqT"	"33-820-388-8545"	" express, final pinto beans. ironic, final requests sleep. furiously final ideas acros"
2577.83	"Sarabharajudara#000007492"	"ROMANIA                  "	22487	"Manufacturer#4           "	"j4GTlT,MQlEPWsuSNUx0k7p"	"29-660-153-6870"	"y even pinto beans. blithely eve"
2577.83	"Sarabharajudara#000007492"	"ROMANIA                  "	22487	"Manufacturer#4           "	"j4GTlT,MQlEPWsuSNUx0k7p"	"29-660-153-6870"	"y even pinto beans. blithely eve"
2560.12	"Sarabharajudara#000002676"	"FRANCE                   "	5175	"Manufacturer#3           "	"Xl4TnYEpX4JlkQh11gL8hXTYRQ1"	"16-262-321-9209"	"ickly excuses. final packages detect blithely regular ideas. never even acco"
2560.12	"Sarabharajudara#000002676"	"FRANCE                   "	5175	"Manufacturer#3           "	"Xl4TnYEpX4JlkQh11gL8hXTYRQ1"	"16-262-321-9209"	"ickly excuses. final packages detect blithely regular ideas. never even acco"
2489.75	"Sarabharajudara#000006855"	"RUSSIA                   "	6854	"Manufacturer#4           "	"ytCDS VWibP"	"32-285-557-7800"	"ly regular deposits boost. slyly bold theodolites wake blithely. furiously even pinto beans thras"
2489.75	"Sarabharajudara#000006855"	"RUSSIA                   "	6854	"Manufacturer#4           "	"ytCDS VWibP"	"32-285-557-7800"	"ly regular deposits boost. slyly bold theodolites wake blithely. furiously even pinto beans thras"
2489.75	"Sarabharajudara#000006855"	"RUSSIA                   "	94345	"Manufacturer#4           "	"ytCDS VWibP"	"32-285-557-7800"	"ly regular deposits boost. slyly bold theodolites wake blithely. furiously even pinto beans thras"
2489.75	"Sarabharajudara#000006855"	"RUSSIA                   "	94345	"Manufacturer#4           "	"ytCDS VWibP"	"32-285-557-7800"	"ly regular deposits boost. slyly bold theodolites wake blithely. furiously even pinto beans thras"
2462.97	"Sarabharajudara#000000711"	"ROMANIA                  "	83186	"Manufacturer#1           "	"oG9,,CGt6x5c sDr1tzAdzvq1y"	"29-291-385-3264"	"ts. blithely special dependencies i"
2462.97	"Sarabharajudara#000000711"	"ROMANIA                  "	83186	"Manufacturer#1           "	"oG9,,CGt6x5c sDr1tzAdzvq1y"	"29-291-385-3264"	"ts. blithely special dependencies i"
2461.34	"Sarabharajudara#000007732"	"ROMANIA                  "	45227	"Manufacturer#2           "	"QsUb05sYrP2amzq63xfTs9MKNTX ju0hIcC8 a"	"29-294-874-5655"	" bold pinto beans cajole quickly after the foxes. quickly regular "
2461.34	"Sarabharajudara#000007732"	"ROMANIA                  "	45227	"Manufacturer#2           "	"QsUb05sYrP2amzq63xfTs9MKNTX ju0hIcC8 a"	"29-294-874-5655"	" bold pinto beans cajole quickly after the foxes. quickly regular "
2417.08	"Sarabharajudara#000006082"	"UNITED KINGDOM           "	176081	"Manufacturer#3           "	"ziRmQdcZa3QENhR364dVXMfJXRX2Nk"	"33-685-737-1893"	"ose asymptotes boost carefully carefully final requests. furi"
2417.08	"Sarabharajudara#000006082"	"UNITED KINGDOM           "	176081	"Manufacturer#3           "	"ziRmQdcZa3QENhR364dVXMfJXRX2Nk"	"33-685-737-1893"	"ose asymptotes boost carefully carefully final requests. furi"
2393.52	"Sarabharajudara#000006715"	"ROMANIA                  "	31708	"Manufacturer#5           "	"SX47Fkv7ADR9IhG6mMDRaGuRcSyjMRi3A3ex5,"	"29-811-331-7891"	"nic packages. blithely regular deposits according to the slyl"
2393.52	"Sarabharajudara#000006715"	"ROMANIA                  "	31708	"Manufacturer#5           "	"SX47Fkv7ADR9IhG6mMDRaGuRcSyjMRi3A3ex5,"	"29-811-331-7891"	"nic packages. blithely regular deposits according to the slyl"
2373.81	"Sarabharajudara#000009697"	"UNITED KINGDOM           "	144668	"Manufacturer#2           "	"o2X 3GLhipvp1ReLO7EcBlz13MI"	"33-323-107-8373"	"al requests: slyly regular foxes must detect carefully pending, eve"
2373.81	"Sarabharajudara#000009697"	"UNITED KINGDOM           "	144668	"Manufacturer#2           "	"o2X 3GLhipvp1ReLO7EcBlz13MI"	"33-323-107-8373"	"al requests: slyly regular foxes must detect carefully pending, eve"
2359.12	"Sarabharajudara#000009568"	"UNITED KINGDOM           "	109567	"Manufacturer#3           "	"YnMsjNT7FDi"	"33-436-335-8486"	"across the ironic waters. slyly bold pinto beans are carefully express deposits. f"
2359.12	"Sarabharajudara#000009568"	"UNITED KINGDOM           "	109567	"Manufacturer#3           "	"YnMsjNT7FDi"	"33-436-335-8486"	"across the ironic waters. slyly bold pinto beans are carefully express deposits. f"
2357.54	"Sarabharajudara#000003513"	"RUSSIA                   "	26006	"Manufacturer#3           "	"Rj i6dgjYQlM3bQiDcbGg Ax90RggjVqhSjwnI,n"	"32-912-584-5642"	"s print fluffily. slyly unusual dependencies are. instructions sleep furiously. ironic, bold p"
2357.54	"Sarabharajudara#000003513"	"RUSSIA                   "	26006	"Manufacturer#3           "	"Rj i6dgjYQlM3bQiDcbGg Ax90RggjVqhSjwnI,n"	"32-912-584-5642"	"s print fluffily. slyly unusual dependencies are. instructions sleep furiously. ironic, bold p"
2286.14	"Sarabharajudara#000004420"	"GERMANY                  "	104419	"Manufacturer#2           "	"HnfTtxqicsm3JSus2KuVLWDit"	"17-860-214-1250"	" to the slyly ironic theodolites."
2286.14	"Sarabharajudara#000004420"	"GERMANY                  "	104419	"Manufacturer#2           "	"HnfTtxqicsm3JSus2KuVLWDit"	"17-860-214-1250"	" to the slyly ironic theodolites."
2218.15	"Sarabharajudara#000006586"	"RUSSIA                   "	156585	"Manufacturer#1           "	"PW7VOUWGU RVU0Et89FHHc84"	"32-959-302-3652"	"ic platelets. slyly special pinto beans haggle bl"
2218.15	"Sarabharajudara#000006586"	"RUSSIA                   "	156585	"Manufacturer#1           "	"PW7VOUWGU RVU0Et89FHHc84"	"32-959-302-3652"	"ic platelets. slyly special pinto beans haggle bl"
2217.93	"Sarabharajudara#000000139"	"RUSSIA                   "	122602	"Manufacturer#1           "	" 2mQLQsVJ8WLBSnl0R bXrcyTgqXKrplgxb"	"32-788-265-2743"	"arefully ironic ideas: slyly regular deposits about the furiously ironic requests"
2217.93	"Sarabharajudara#000000139"	"RUSSIA                   "	122602	"Manufacturer#1           "	" 2mQLQsVJ8WLBSnl0R bXrcyTgqXKrplgxb"	"32-788-265-2743"	"arefully ironic ideas: slyly regular deposits about the furiously ironic requests"
2172.62	"Sarabharajudara#000006279"	"UNITED KINGDOM           "	11276	"Manufacturer#2           "	"pN2YG7qZBGsVUe8F"	"33-526-284-6953"	"final accounts. carefully even dolphins against t"
2172.62	"Sarabharajudara#000006279"	"UNITED KINGDOM           "	11276	"Manufacturer#2           "	"pN2YG7qZBGsVUe8F"	"33-526-284-6953"	"final accounts. carefully even dolphins against t"
2172.42	"Sarabharajudara#000003814"	"UNITED KINGDOM           "	166265	"Manufacturer#2           "	"vTnXsG9KzNlsiO6tpbL6fp7"	"33-280-183-9315"	"efully regular platelets. fluffily slow asymptotes alongside of the spe"
2172.42	"Sarabharajudara#000003814"	"UNITED KINGDOM           "	166265	"Manufacturer#2           "	"vTnXsG9KzNlsiO6tpbL6fp7"	"33-280-183-9315"	"efully regular platelets. fluffily slow asymptotes alongside of the spe"
2152.17	"Sarabharajudara#000002294"	"RUSSIA                   "	29791	"Manufacturer#3           "	"dcAWrWvBzWRQ8j2lUMRKol3Eq,4xFipvykrHfu"	"32-342-857-4948"	"packages haggle carefully. quickly expres"
2152.17	"Sarabharajudara#000002294"	"RUSSIA                   "	29791	"Manufacturer#3           "	"dcAWrWvBzWRQ8j2lUMRKol3Eq,4xFipvykrHfu"	"32-342-857-4948"	"packages haggle carefully. quickly expres"
2152.17	"Sarabharajudara#000002294"	"RUSSIA                   "	47285	"Manufacturer#4           "	"dcAWrWvBzWRQ8j2lUMRKol3Eq,4xFipvykrHfu"	"32-342-857-4948"	"packages haggle carefully. quickly expres"
2152.17	"Sarabharajudara#000002294"	"RUSSIA                   "	47285	"Manufacturer#4           "	"dcAWrWvBzWRQ8j2lUMRKol3Eq,4xFipvykrHfu"	"32-342-857-4948"	"packages haggle carefully. quickly expres"
2077.39	"Sarabharajudara#000000172"	"RUSSIA                   "	60171	"Manufacturer#4           "	"NckigAXBRUXbJI"	"32-481-329-1585"	"efully ironic packages x-ray thinly. slyly pending hockey players haggle slyly. sly"
2077.39	"Sarabharajudara#000000172"	"RUSSIA                   "	60171	"Manufacturer#4           "	"NckigAXBRUXbJI"	"32-481-329-1585"	"efully ironic packages x-ray thinly. slyly pending hockey players haggle slyly. sly"
2077.39	"Sarabharajudara#000000172"	"RUSSIA                   "	100171	"Manufacturer#1           "	"NckigAXBRUXbJI"	"32-481-329-1585"	"efully ironic packages x-ray thinly. slyly pending hockey players haggle slyly. sly"
2077.39	"Sarabharajudara#000000172"	"RUSSIA                   "	100171	"Manufacturer#1           "	"NckigAXBRUXbJI"	"32-481-329-1585"	"efully ironic packages x-ray thinly. slyly pending hockey players haggle slyly. sly"
1981.07	"Sarabharajudara#000002653"	"UNITED KINGDOM           "	87636	"Manufacturer#1           "	"QhF5puAJxt yLg4px2"	"33-387-651-1873"	"c requests detect accounts. carefully even requests sleep about "
1981.07	"Sarabharajudara#000002653"	"UNITED KINGDOM           "	87636	"Manufacturer#1           "	"QhF5puAJxt yLg4px2"	"33-387-651-1873"	"c requests detect accounts. carefully even requests sleep about "
1927.21	"Sarabharajudara#000000649"	"GERMANY                  "	170648	"Manufacturer#4           "	"8sfoyPTvZbFMXC93ti9qSI6dYN0QuXh3wO"	"17-341-611-2596"	"equests. ironic dependencies are quickly slyl"
1927.21	"Sarabharajudara#000000649"	"GERMANY                  "	170648	"Manufacturer#4           "	"8sfoyPTvZbFMXC93ti9qSI6dYN0QuXh3wO"	"17-341-611-2596"	"equests. ironic dependencies are quickly slyl"
1925.83	"Sarabharajudara#000006340"	"FRANCE                   "	21335	"Manufacturer#4           "	"p9pZspXKY4PcoUOSic2x0FGF65IuJNxtd1"	"16-656-270-4190"	"even realms according to the carefully reg"
1925.83	"Sarabharajudara#000006340"	"FRANCE                   "	21335	"Manufacturer#4           "	"p9pZspXKY4PcoUOSic2x0FGF65IuJNxtd1"	"16-656-270-4190"	"even realms according to the carefully reg"
1896.00	"Sarabharajudara#000003105"	"ROMANIA                  "	60598	"Manufacturer#2           "	"oY9vcEXgL9I3zNx9tukxzCQ98MAyvf30DPzJmxP"	"29-831-521-6983"	" unusual accounts. slyly even dependencies unwind. ironic requests past the carefully pe"
1896.00	"Sarabharajudara#000003105"	"ROMANIA                  "	60598	"Manufacturer#2           "	"oY9vcEXgL9I3zNx9tukxzCQ98MAyvf30DPzJmxP"	"29-831-521-6983"	" unusual accounts. slyly even dependencies unwind. ironic requests past the carefully pe"
1855.07	"Sarabharajudara#000009034"	"GERMANY                  "	161485	"Manufacturer#5           "	"oi,JOa0LITaOToR5L,G1eMDN8ZuhLERVo,3O,2"	"17-351-274-7494"	"l accounts haggle quietly across t"
1855.07	"Sarabharajudara#000009034"	"GERMANY                  "	161485	"Manufacturer#5           "	"oi,JOa0LITaOToR5L,G1eMDN8ZuhLERVo,3O,2"	"17-351-274-7494"	"l accounts haggle quietly across t"
1853.10	"Sarabharajudara#000006320"	"RUSSIA                   "	148777	"Manufacturer#4           "	" YRjdYgv6q8NpX"	"32-211-274-3030"	"uickly ironic packages. quickly expre"
1853.10	"Sarabharajudara#000006320"	"RUSSIA                   "	148777	"Manufacturer#4           "	" YRjdYgv6q8NpX"	"32-211-274-3030"	"uickly ironic packages. quickly expre"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	39005	"Manufacturer#2           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	39005	"Manufacturer#2           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	66514	"Manufacturer#4           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	66514	"Manufacturer#4           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	158969	"Manufacturer#2           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1831.99	"Sarabharajudara#000006515"	"ROMANIA                  "	158969	"Manufacturer#2           "	"n1HaaAgnJXyq0uOJUPZc4OtR6dFab998dsj5ojW"	"29-985-947-8800"	"ts. slyly final requests cajole slyly express, special the"
1827.47	"Sarabharajudara#000006328"	"ROMANIA                  "	16327	"Manufacturer#1           "	"10nuH u4FoWGNY"	"29-734-302-5442"	"luffily even instructions. special instructions pl"
1827.47	"Sarabharajudara#000006328"	"ROMANIA                  "	16327	"Manufacturer#1           "	"10nuH u4FoWGNY"	"29-734-302-5442"	"luffily even instructions. special instructions pl"
1736.47	"Sarabharajudara#000000885"	"GERMANY                  "	130884	"Manufacturer#4           "	"aJUXiGC6qSAWr0Dl0VBahtF"	"17-578-639-8695"	" furiously. carefully pending pin"
1736.47	"Sarabharajudara#000000885"	"GERMANY                  "	130884	"Manufacturer#4           "	"aJUXiGC6qSAWr0Dl0VBahtF"	"17-578-639-8695"	" furiously. carefully pending pin"
1631.83	"Sarabharajudara#000006658"	"UNITED KINGDOM           "	56657	"Manufacturer#3           "	"h25j,DUjfGv9,N1iHhAP"	"33-754-729-1888"	"ronic packages. bravely silent account"
1631.83	"Sarabharajudara#000006658"	"UNITED KINGDOM           "	56657	"Manufacturer#3           "	"h25j,DUjfGv9,N1iHhAP"	"33-754-729-1888"	"ronic packages. bravely silent account"
1607.30	"Sarabharajudara#000008553"	"FRANCE                   "	41040	"Manufacturer#4           "	"9cfBlcQUuHiVY C nhZs5C13ALqXrY0J"	"16-919-476-6611"	"regular ideas was slyly silent epitaphs. fluffily fina"
1607.30	"Sarabharajudara#000008553"	"FRANCE                   "	41040	"Manufacturer#4           "	"9cfBlcQUuHiVY C nhZs5C13ALqXrY0J"	"16-919-476-6611"	"regular ideas was slyly silent epitaphs. fluffily fina"
1596.44	"Sarabharajudara#000000158"	"GERMANY                  "	25153	"Manufacturer#4           "	" fkjbx7,DYi"	"17-873-902-6175"	"cuses sleep after the pending, final "
1596.44	"Sarabharajudara#000000158"	"GERMANY                  "	25153	"Manufacturer#4           "	" fkjbx7,DYi"	"17-873-902-6175"	"cuses sleep after the pending, final "
1559.42	"Sarabharajudara#000005174"	"FRANCE                   "	112662	"Manufacturer#5           "	"ZeXBGYhZj,uAq8m5gyYWM8"	"16-284-735-1835"	"blithely. doggedly bold deposits sleep bold, silent excuses. bold ideas affix. care"
1559.42	"Sarabharajudara#000005174"	"FRANCE                   "	112662	"Manufacturer#5           "	"ZeXBGYhZj,uAq8m5gyYWM8"	"16-284-735-1835"	"blithely. doggedly bold deposits sleep bold, silent excuses. bold ideas affix. care"
1555.70	"Sarabharajudara#000003784"	"ROMANIA                  "	101273	"Manufacturer#5           "	"vmlB8fQ1MaX81ohCxe"	"29-420-513-9188"	"unts haggle evenly final requests. carefully final accounts nag quickly acro"
1555.70	"Sarabharajudara#000003784"	"ROMANIA                  "	101273	"Manufacturer#5           "	"vmlB8fQ1MaX81ohCxe"	"29-420-513-9188"	"unts haggle evenly final requests. carefully final accounts nag quickly acro"
1549.49	"Sarabharajudara#000005018"	"FRANCE                   "	50007	"Manufacturer#2           "	"VF3jw0xQDHivHYnRt9JajvTSsxJxjnD8YY8"	"16-544-227-4448"	"ests integrate slyly pending deposits. slyly dogged platelets above the blithely ironic pinto beans "
1549.49	"Sarabharajudara#000005018"	"FRANCE                   "	50007	"Manufacturer#2           "	"VF3jw0xQDHivHYnRt9JajvTSsxJxjnD8YY8"	"16-544-227-4448"	"ests integrate slyly pending deposits. slyly dogged platelets above the blithely ironic pinto beans "
1547.92	"Sarabharajudara#000003799"	"GERMANY                  "	176247	"Manufacturer#3           "	"fFNV7NiIdwh7uMK"	"17-660-903-4812"	"l ideas upon the busily final pinto beans cajole thinly along the accounts."
1547.92	"Sarabharajudara#000003799"	"GERMANY                  "	176247	"Manufacturer#3           "	"fFNV7NiIdwh7uMK"	"17-660-903-4812"	"l ideas upon the busily final pinto beans cajole thinly along the accounts."
1545.16	"Sarabharajudara#000005827"	"RUSSIA                   "	13325	"Manufacturer#1           "	"O,abBOMPP,r4"	"32-146-400-6420"	"after the furiously even requests-- ironic, final accounts wake slyly alongside of the blith"
1545.16	"Sarabharajudara#000005827"	"RUSSIA                   "	13325	"Manufacturer#1           "	"O,abBOMPP,r4"	"32-146-400-6420"	"after the furiously even requests-- ironic, final accounts wake slyly alongside of the blith"
1545.16	"Sarabharajudara#000005827"	"RUSSIA                   "	123314	"Manufacturer#2           "	"O,abBOMPP,r4"	"32-146-400-6420"	"after the furiously even requests-- ironic, final accounts wake slyly alongside of the blith"
1545.16	"Sarabharajudara#000005827"	"RUSSIA                   "	123314	"Manufacturer#2           "	"O,abBOMPP,r4"	"32-146-400-6420"	"after the furiously even requests-- ironic, final accounts wake slyly alongside of the blith"
1417.33	"Sarabharajudara#000007386"	"RUSSIA                   "	129849	"Manufacturer#3           "	"7OwCfIcamhJtcgiTUcUq0lMGzVT0CWmZvq245G"	"32-799-168-3188"	" courts sleep bravely furiously even asymptotes. furiously"
1417.33	"Sarabharajudara#000007386"	"RUSSIA                   "	129849	"Manufacturer#3           "	"7OwCfIcamhJtcgiTUcUq0lMGzVT0CWmZvq245G"	"32-799-168-3188"	" courts sleep bravely furiously even asymptotes. furiously"
1417.33	"Sarabharajudara#000007386"	"RUSSIA                   "	144871	"Manufacturer#2           "	"7OwCfIcamhJtcgiTUcUq0lMGzVT0CWmZvq245G"	"32-799-168-3188"	" courts sleep bravely furiously even asymptotes. furiously"
1417.33	"Sarabharajudara#000007386"	"RUSSIA                   "	144871	"Manufacturer#2           "	"7OwCfIcamhJtcgiTUcUq0lMGzVT0CWmZvq245G"	"32-799-168-3188"	" courts sleep bravely furiously even asymptotes. furiously"
1392.40	"Sarabharajudara#000008623"	"ROMANIA                  "	38622	"Manufacturer#4           "	"F8LwoBXK01DqdKGPkaHVwltbz58R"	"29-265-595-4732"	"inal, final deposits. foxes "
1392.40	"Sarabharajudara#000008623"	"ROMANIA                  "	38622	"Manufacturer#4           "	"F8LwoBXK01DqdKGPkaHVwltbz58R"	"29-265-595-4732"	"inal, final deposits. foxes "
1392.40	"Sarabharajudara#000008623"	"ROMANIA                  "	191065	"Manufacturer#4           "	"F8LwoBXK01DqdKGPkaHVwltbz58R"	"29-265-595-4732"	"inal, final deposits. foxes "
1392.40	"Sarabharajudara#000008623"	"ROMANIA                  "	191065	"Manufacturer#4           "	"F8LwoBXK01DqdKGPkaHVwltbz58R"	"29-265-595-4732"	"inal, final deposits. foxes "
1379.73	"Sarabharajudara#000002955"	"ROMANIA                  "	25448	"Manufacturer#4           "	"0QYFiINAihBC 2E4"	"29-411-552-9157"	"latelets. ironic asymptotes above the quickly even excuses are quickly across the even reque"
1379.73	"Sarabharajudara#000002955"	"ROMANIA                  "	25448	"Manufacturer#4           "	"0QYFiINAihBC 2E4"	"29-411-552-9157"	"latelets. ironic asymptotes above the quickly even excuses are quickly across the even reque"
1344.52	"Sarabharajudara#000002229"	"RUSSIA                   "	164680	"Manufacturer#3           "	"2i8gsU1RJfqUBJmb6HDEQ4"	"32-273-826-7792"	"instructions nod quickly regular deposits. bold, unusu"
1344.52	"Sarabharajudara#000002229"	"RUSSIA                   "	164680	"Manufacturer#3           "	"2i8gsU1RJfqUBJmb6HDEQ4"	"32-273-826-7792"	"instructions nod quickly regular deposits. bold, unusu"
1317.02	"Sarabharajudara#000004903"	"ROMANIA                  "	64902	"Manufacturer#4           "	"5jqh0004hsIRqM4CBf3ej"	"29-753-806-8134"	" the furiously ironic requests. ironic, regular plate"
1317.02	"Sarabharajudara#000004903"	"ROMANIA                  "	64902	"Manufacturer#4           "	"5jqh0004hsIRqM4CBf3ej"	"29-753-806-8134"	" the furiously ironic requests. ironic, regular plate"
1297.27	"Sarabharajudara#000008915"	"ROMANIA                  "	83898	"Manufacturer#5           "	"5,6vc4drzY8d1YxXJq7"	"29-754-306-3305"	"c deposits sleep slyly slyly idle somas. thinly pending accounts nag carefully alongside of the fi"
1297.27	"Sarabharajudara#000008915"	"ROMANIA                  "	83898	"Manufacturer#5           "	"5,6vc4drzY8d1YxXJq7"	"29-754-306-3305"	"c deposits sleep slyly slyly idle somas. thinly pending accounts nag carefully alongside of the fi"
1294.72	"Sarabharajudara#000005656"	"FRANCE                   "	25655	"Manufacturer#2           "	"nYY vwwWaAuXihpyn"	"16-263-334-4011"	" believe slowly-- deposits boost. furiously pen"
1294.72	"Sarabharajudara#000005656"	"FRANCE                   "	25655	"Manufacturer#2           "	"nYY vwwWaAuXihpyn"	"16-263-334-4011"	" believe slowly-- deposits boost. furiously pen"
1294.72	"Sarabharajudara#000005656"	"FRANCE                   "	95655	"Manufacturer#5           "	"nYY vwwWaAuXihpyn"	"16-263-334-4011"	" believe slowly-- deposits boost. furiously pen"
1294.72	"Sarabharajudara#000005656"	"FRANCE                   "	95655	"Manufacturer#5           "	"nYY vwwWaAuXihpyn"	"16-263-334-4011"	" believe slowly-- deposits boost. furiously pen"
1280.85	"Sarabharajudara#000004021"	"GERMANY                  "	4020	"Manufacturer#1           "	"Q5OtYOoYjsSKUtYlf7DSl,757"	"17-355-893-5738"	"ecial deposits. furious requests engage? fluffily unusual theodolites ea"
1280.85	"Sarabharajudara#000004021"	"GERMANY                  "	4020	"Manufacturer#1           "	"Q5OtYOoYjsSKUtYlf7DSl,757"	"17-355-893-5738"	"ecial deposits. furious requests engage? fluffily unusual theodolites ea"
1273.32	"Sarabharajudara#000008600"	"GERMANY                  "	41087	"Manufacturer#3           "	"ZYFNk9cRM66qHdcrOR8wNNRKQsjh"	"17-389-804-4258"	" silent requests. blithely final foxes haggle slyly at the carefully regula"
1273.32	"Sarabharajudara#000008600"	"GERMANY                  "	41087	"Manufacturer#3           "	"ZYFNk9cRM66qHdcrOR8wNNRKQsjh"	"17-389-804-4258"	" silent requests. blithely final foxes haggle slyly at the carefully regula"
1266.47	"Sarabharajudara#000007490"	"UNITED KINGDOM           "	39980	"Manufacturer#5           "	"4E5gwkoxUw5EPHxUxeP1a0 jVrR jCwR"	"33-581-252-8292"	"ily. carefully quick dependencies cajole. fluffily bold dependencies kindle"
1266.47	"Sarabharajudara#000007490"	"UNITED KINGDOM           "	39980	"Manufacturer#5           "	"4E5gwkoxUw5EPHxUxeP1a0 jVrR jCwR"	"33-581-252-8292"	"ily. carefully quick dependencies cajole. fluffily bold dependencies kindle"
1266.47	"Sarabharajudara#000007490"	"UNITED KINGDOM           "	89965	"Manufacturer#4           "	"4E5gwkoxUw5EPHxUxeP1a0 jVrR jCwR"	"33-581-252-8292"	"ily. carefully quick dependencies cajole. fluffily bold dependencies kindle"
1266.47	"Sarabharajudara#000007490"	"UNITED KINGDOM           "	89965	"Manufacturer#4           "	"4E5gwkoxUw5EPHxUxeP1a0 jVrR jCwR"	"33-581-252-8292"	"ily. carefully quick dependencies cajole. fluffily bold dependencies kindle"
1252.59	"Sarabharajudara#000003298"	"UNITED KINGDOM           "	5797	"Manufacturer#1           "	"gW0OcqV3TD7"	"33-364-207-9726"	"ogs. ironic accounts cajole a"
1252.59	"Sarabharajudara#000003298"	"UNITED KINGDOM           "	5797	"Manufacturer#1           "	"gW0OcqV3TD7"	"33-364-207-9726"	"ogs. ironic accounts cajole a"
1231.69	"Sarabharajudara#000003537"	"ROMANIA                  "	161020	"Manufacturer#5           "	"upAlzbn0gUSW4fq3r2pIn7abaiSedT,7nVqkA"	"29-525-534-3904"	"ever according to the slyly sp"
1231.69	"Sarabharajudara#000003537"	"ROMANIA                  "	161020	"Manufacturer#5           "	"upAlzbn0gUSW4fq3r2pIn7abaiSedT,7nVqkA"	"29-525-534-3904"	"ever according to the slyly sp"
1189.39	"Sarabharajudara#000005771"	"RUSSIA                   "	178219	"Manufacturer#1           "	"wqPmXKZoucEWZM0,6s56AjHoZXi7r6skXoV U"	"32-436-418-7659"	" packages. furiously unusual foxes cajole blithely. regular excuses sleep furiously."
1189.39	"Sarabharajudara#000005771"	"RUSSIA                   "	178219	"Manufacturer#1           "	"wqPmXKZoucEWZM0,6s56AjHoZXi7r6skXoV U"	"32-436-418-7659"	" packages. furiously unusual foxes cajole blithely. regular excuses sleep furiously."
1189.36	"Sarabharajudara#000008166"	"ROMANIA                  "	25663	"Manufacturer#4           "	"VB3HlzNsC R9rUO5GQ"	"29-661-385-7757"	"osits use quickly even ideas. closely unusu"
1189.36	"Sarabharajudara#000008166"	"ROMANIA                  "	25663	"Manufacturer#4           "	"VB3HlzNsC R9rUO5GQ"	"29-661-385-7757"	"osits use quickly even ideas. closely unusu"
1189.36	"Sarabharajudara#000008166"	"ROMANIA                  "	140623	"Manufacturer#1           "	"VB3HlzNsC R9rUO5GQ"	"29-661-385-7757"	"osits use quickly even ideas. closely unusu"
1189.36	"Sarabharajudara#000008166"	"ROMANIA                  "	140623	"Manufacturer#1           "	"VB3HlzNsC R9rUO5GQ"	"29-661-385-7757"	"osits use quickly even ideas. closely unusu"
1152.96	"Sarabharajudara#000007582"	"FRANCE                   "	10078	"Manufacturer#1           "	"XhM0z6DsdvpXzo4Xe67e"	"16-246-633-4829"	"nticingly even pinto beans. furiously ironic packages above the thinly"
1152.96	"Sarabharajudara#000007582"	"FRANCE                   "	10078	"Manufacturer#1           "	"XhM0z6DsdvpXzo4Xe67e"	"16-246-633-4829"	"nticingly even pinto beans. furiously ironic packages above the thinly"
1137.30	"Sarabharajudara#000004928"	"ROMANIA                  "	87403	"Manufacturer#2           "	"IYpwXYEo2yIkLowAPbV41 oR"	"29-801-741-2301"	"leep. quickly silent excuses cajole among th"
1137.30	"Sarabharajudara#000004928"	"ROMANIA                  "	87403	"Manufacturer#2           "	"IYpwXYEo2yIkLowAPbV41 oR"	"29-801-741-2301"	"leep. quickly silent excuses cajole among th"
1133.80	"Sarabharajudara#000000634"	"UNITED KINGDOM           "	38130	"Manufacturer#5           "	"hS62vraooyHWnMKyZV3f1GSPeKJ,7uRK6M5"	"33-105-608-2902"	"equests affix around the blithely special theodolites. unusual accounts wake. pend"
1133.80	"Sarabharajudara#000000634"	"UNITED KINGDOM           "	38130	"Manufacturer#5           "	"hS62vraooyHWnMKyZV3f1GSPeKJ,7uRK6M5"	"33-105-608-2902"	"equests affix around the blithely special theodolites. unusual accounts wake. pend"
1039.23	"Sarabharajudara#000009836"	"RUSSIA                   "	177318	"Manufacturer#2           "	"vKVMlivaUCeWpMkzYafVd"	"32-457-649-5465"	". ironic, final instructions nag quickly. bold instructions use q"
1039.23	"Sarabharajudara#000009836"	"RUSSIA                   "	177318	"Manufacturer#2           "	"vKVMlivaUCeWpMkzYafVd"	"32-457-649-5465"	". ironic, final instructions nag quickly. bold instructions use q"
978.84	"Sarabharajudara#000006129"	"FRANCE                   "	151098	"Manufacturer#3           "	"SeYweH 5LLy, 7 y0C"	"16-373-131-7534"	"ven somas. furiously final pinto beans breach according to"
978.84	"Sarabharajudara#000006129"	"FRANCE                   "	151098	"Manufacturer#3           "	"SeYweH 5LLy, 7 y0C"	"16-373-131-7534"	"ven somas. furiously final pinto beans breach according to"
966.76	"Sarabharajudara#000002442"	"ROMANIA                  "	109931	"Manufacturer#2           "	"t73nwMfpO4rjUFkhWnJcS09dBCR"	"29-971-643-5013"	"even packages. unusual, regular deposits are about the regular dependencies. slyly sp"
966.76	"Sarabharajudara#000002442"	"ROMANIA                  "	109931	"Manufacturer#2           "	"t73nwMfpO4rjUFkhWnJcS09dBCR"	"29-971-643-5013"	"even packages. unusual, regular deposits are about the regular dependencies. slyly sp"
957.59	"Sarabharajudara#000003586"	"ROMANIA                  "	73585	"Manufacturer#4           "	"OxKA5gwi VkWgSf8r4ZUx5KWqMdeaYKQZ"	"29-223-914-6598"	"uffily according to the express acco"
957.59	"Sarabharajudara#000003586"	"ROMANIA                  "	73585	"Manufacturer#4           "	"OxKA5gwi VkWgSf8r4ZUx5KWqMdeaYKQZ"	"29-223-914-6598"	"uffily according to the express acco"
906.07	"Sarabharajudara#000000138"	"ROMANIA                  "	67631	"Manufacturer#2           "	"utbplAm g7RmxVfYoNdhcrQGWuzRqPe0qHSwbKw"	"29-533-434-6776"	"ickly unusual requests cajole. accounts above the furiously special excuses "
906.07	"Sarabharajudara#000000138"	"ROMANIA                  "	67631	"Manufacturer#2           "	"utbplAm g7RmxVfYoNdhcrQGWuzRqPe0qHSwbKw"	"29-533-434-6776"	"ickly unusual requests cajole. accounts above the furiously special excuses "
830.73	"Sarabharajudara#000007148"	"ROMANIA                  "	34644	"Manufacturer#5           "	"FDxytVBVJllKW"	"29-216-866-2808"	"lyly above the furiously busy foxes. express ideas use carefully after th"
830.73	"Sarabharajudara#000007148"	"ROMANIA                  "	34644	"Manufacturer#5           "	"FDxytVBVJllKW"	"29-216-866-2808"	"lyly above the furiously busy foxes. express ideas use carefully after th"
781.51	"Sarabharajudara#000008081"	"FRANCE                   "	3080	"Manufacturer#2           "	"a1xOE WQzn,nGC5kBzKRdWxI2cl0D2q"	"16-623-963-9556"	"along the carefully pending packages. slyly ironic depen"
781.51	"Sarabharajudara#000008081"	"FRANCE                   "	3080	"Manufacturer#2           "	"a1xOE WQzn,nGC5kBzKRdWxI2cl0D2q"	"16-623-963-9556"	"along the carefully pending packages. slyly ironic depen"
771.33	"Sarabharajudara#000003276"	"ROMANIA                  "	13275	"Manufacturer#4           "	"dIPRD9Z7blDleqsnNfGF"	"29-181-839-9372"	"sly final pinto beans nag furiously pinto be"
771.33	"Sarabharajudara#000003276"	"ROMANIA                  "	13275	"Manufacturer#4           "	"dIPRD9Z7blDleqsnNfGF"	"29-181-839-9372"	"sly final pinto beans nag furiously pinto be"
771.33	"Sarabharajudara#000003276"	"ROMANIA                  "	43275	"Manufacturer#1           "	"dIPRD9Z7blDleqsnNfGF"	"29-181-839-9372"	"sly final pinto beans nag furiously pinto be"
771.33	"Sarabharajudara#000003276"	"ROMANIA                  "	43275	"Manufacturer#1           "	"dIPRD9Z7blDleqsnNfGF"	"29-181-839-9372"	"sly final pinto beans nag furiously pinto be"
766.64	"Sarabharajudara#000008035"	"RUSSIA                   "	115523	"Manufacturer#3           "	",zLgenfT0jr16MbjJt 9WfCU6xm2N3hQy79Migc"	"32-321-763-7850"	"ously. regular packages kindle blithely furio"
766.64	"Sarabharajudara#000008035"	"RUSSIA                   "	115523	"Manufacturer#3           "	",zLgenfT0jr16MbjJt 9WfCU6xm2N3hQy79Migc"	"32-321-763-7850"	"ously. regular packages kindle blithely furio"
723.12	"Sarabharajudara#000002112"	"ROMANIA                  "	74590	"Manufacturer#3           "	"McUW2in3FZWMkplg"	"29-740-945-1203"	". packages wake furiously. "
723.12	"Sarabharajudara#000002112"	"ROMANIA                  "	74590	"Manufacturer#3           "	"McUW2in3FZWMkplg"	"29-740-945-1203"	". packages wake furiously. "
700.51	"Sarabharajudara#000006267"	"FRANCE                   "	81250	"Manufacturer#1           "	"UB0y3o3xdo02Xy55mK2qcIdv5ZJh88aE3EQRGHWL"	"16-460-193-2006"	" slyly blithely silent asymptotes. foxes nag carefully pending deposits. furiously e"
700.51	"Sarabharajudara#000006267"	"FRANCE                   "	81250	"Manufacturer#1           "	"UB0y3o3xdo02Xy55mK2qcIdv5ZJh88aE3EQRGHWL"	"16-460-193-2006"	" slyly blithely silent asymptotes. foxes nag carefully pending deposits. furiously e"
686.50	"Sarabharajudara#000001731"	"GERMANY                  "	109220	"Manufacturer#4           "	"Dqy8LQtY5i8GygrdOC1lt,OVsIgrGoL8Z3PMs"	"17-115-638-8685"	"lar requests. final, final platelets around the carefully even deposi"
686.50	"Sarabharajudara#000001731"	"GERMANY                  "	109220	"Manufacturer#4           "	"Dqy8LQtY5i8GygrdOC1lt,OVsIgrGoL8Z3PMs"	"17-115-638-8685"	"lar requests. final, final platelets around the carefully even deposi"
686.50	"Sarabharajudara#000001731"	"GERMANY                  "	186694	"Manufacturer#4           "	"Dqy8LQtY5i8GygrdOC1lt,OVsIgrGoL8Z3PMs"	"17-115-638-8685"	"lar requests. final, final platelets around the carefully even deposi"
686.50	"Sarabharajudara#000001731"	"GERMANY                  "	186694	"Manufacturer#4           "	"Dqy8LQtY5i8GygrdOC1lt,OVsIgrGoL8Z3PMs"	"17-115-638-8685"	"lar requests. final, final platelets around the carefully even deposi"
679.51	"Sarabharajudara#000008946"	"RUSSIA                   "	86437	"Manufacturer#3           "	"H5GRyJBvI3mZJ6w,1Qp82ioQR7Q WWWTR4qa0"	"32-556-539-1611"	" about the silently regular packages integrate furiously about"
679.51	"Sarabharajudara#000008946"	"RUSSIA                   "	86437	"Manufacturer#3           "	"H5GRyJBvI3mZJ6w,1Qp82ioQR7Q WWWTR4qa0"	"32-556-539-1611"	" about the silently regular packages integrate furiously about"
673.78	"Sarabharajudara#000001571"	"UNITED KINGDOM           "	161570	"Manufacturer#4           "	"08Pd2gUuOUK8aRZiHWv0IDCP1 ZIkxIt5"	"33-273-607-3674"	"hely above the regular foxes. deposits print never quickly even deposits. regul"
673.78	"Sarabharajudara#000001571"	"UNITED KINGDOM           "	161570	"Manufacturer#4           "	"08Pd2gUuOUK8aRZiHWv0IDCP1 ZIkxIt5"	"33-273-607-3674"	"hely above the regular foxes. deposits print never quickly even deposits. regul"
629.43	"Sarabharajudara#000004835"	"UNITED KINGDOM           "	17331	"Manufacturer#2           "	"yAvaoHJQHGbWRhcBrGJAhyqf5PAq1jruZIo LzM"	"33-760-622-5299"	"ang slyly atop the instructions. slyly final accounts dazzle carefully above"
629.43	"Sarabharajudara#000004835"	"UNITED KINGDOM           "	17331	"Manufacturer#2           "	"yAvaoHJQHGbWRhcBrGJAhyqf5PAq1jruZIo LzM"	"33-760-622-5299"	"ang slyly atop the instructions. slyly final accounts dazzle carefully above"
629.43	"Sarabharajudara#000004835"	"UNITED KINGDOM           "	194834	"Manufacturer#1           "	"yAvaoHJQHGbWRhcBrGJAhyqf5PAq1jruZIo LzM"	"33-760-622-5299"	"ang slyly atop the instructions. slyly final accounts dazzle carefully above"
629.43	"Sarabharajudara#000004835"	"UNITED KINGDOM           "	194834	"Manufacturer#1           "	"yAvaoHJQHGbWRhcBrGJAhyqf5PAq1jruZIo LzM"	"33-760-622-5299"	"ang slyly atop the instructions. slyly final accounts dazzle carefully above"
614.57	"Sarabharajudara#000000580"	"FRANCE                   "	73058	"Manufacturer#4           "	"MuRScZH74veaM2"	"16-732-277-6239"	"packages. furiously final theodolites integrate according to the carefully silent braids. caref"
614.57	"Sarabharajudara#000000580"	"FRANCE                   "	73058	"Manufacturer#4           "	"MuRScZH74veaM2"	"16-732-277-6239"	"packages. furiously final theodolites integrate according to the carefully silent braids. caref"
562.16	"Sarabharajudara#000006164"	"UNITED KINGDOM           "	191125	"Manufacturer#5           "	"PwJeAuYCoZGaYAPw7W"	"33-725-717-4417"	"ic theodolites affix foxe"
562.16	"Sarabharajudara#000006164"	"UNITED KINGDOM           "	191125	"Manufacturer#5           "	"PwJeAuYCoZGaYAPw7W"	"33-725-717-4417"	"ic theodolites affix foxe"
555.18	"Sarabharajudara#000002931"	"GERMANY                  "	12930	"Manufacturer#3           "	"aUivhoesqMqv0FmJcPBMxBSl8DJvXBGj"	"17-905-318-3455"	"t the fluffily ironic packages wake furiously "
555.18	"Sarabharajudara#000002931"	"GERMANY                  "	12930	"Manufacturer#3           "	"aUivhoesqMqv0FmJcPBMxBSl8DJvXBGj"	"17-905-318-3455"	"t the fluffily ironic packages wake furiously "
555.18	"Sarabharajudara#000002931"	"GERMANY                  "	20428	"Manufacturer#4           "	"aUivhoesqMqv0FmJcPBMxBSl8DJvXBGj"	"17-905-318-3455"	"t the fluffily ironic packages wake furiously "
555.18	"Sarabharajudara#000002931"	"GERMANY                  "	20428	"Manufacturer#4           "	"aUivhoesqMqv0FmJcPBMxBSl8DJvXBGj"	"17-905-318-3455"	"t the fluffily ironic packages wake furiously "
549.24	"Sarabharajudara#000007819"	"RUSSIA                   "	112796	"Manufacturer#1           "	"hw 95lkhhkNUIq3cYuctCfjlUOU"	"32-111-417-1890"	"ngside of the final dolphi"
549.24	"Sarabharajudara#000007819"	"RUSSIA                   "	112796	"Manufacturer#1           "	"hw 95lkhhkNUIq3cYuctCfjlUOU"	"32-111-417-1890"	"ngside of the final dolphi"
547.09	"Sarabharajudara#000007436"	"RUSSIA                   "	42427	"Manufacturer#4           "	"HVuRAb35M6j82A2hPcibeLKzo"	"32-791-422-6015"	"y. silent excuses with the quickly even dependencies hinde"
547.09	"Sarabharajudara#000007436"	"RUSSIA                   "	42427	"Manufacturer#4           "	"HVuRAb35M6j82A2hPcibeLKzo"	"32-791-422-6015"	"y. silent excuses with the quickly even dependencies hinde"
547.09	"Sarabharajudara#000007436"	"RUSSIA                   "	149893	"Manufacturer#2           "	"HVuRAb35M6j82A2hPcibeLKzo"	"32-791-422-6015"	"y. silent excuses with the quickly even dependencies hinde"
547.09	"Sarabharajudara#000007436"	"RUSSIA                   "	149893	"Manufacturer#2           "	"HVuRAb35M6j82A2hPcibeLKzo"	"32-791-422-6015"	"y. silent excuses with the quickly even dependencies hinde"
533.65	"Sarabharajudara#000002588"	"ROMANIA                  "	12587	"Manufacturer#1           "	"QBDXWHsFbL43hT6gqU4ynyr0PrIr,sl2"	"29-974-158-2888"	"lessly special deposits cajole. carefully regular deposits would nag furiously"
533.65	"Sarabharajudara#000002588"	"ROMANIA                  "	12587	"Manufacturer#1           "	"QBDXWHsFbL43hT6gqU4ynyr0PrIr,sl2"	"29-974-158-2888"	"lessly special deposits cajole. carefully regular deposits would nag furiously"
519.24	"Sarabharajudara#000006844"	"GERMANY                  "	31837	"Manufacturer#3           "	"I5Zl4KJ7 A7,ZELv Hrxca"	"17-123-209-1299"	"quests boost. blithely regular ideas haggle carefully accounts. express, idle accounts are. caref"
519.24	"Sarabharajudara#000006844"	"GERMANY                  "	31837	"Manufacturer#3           "	"I5Zl4KJ7 A7,ZELv Hrxca"	"17-123-209-1299"	"quests boost. blithely regular ideas haggle carefully accounts. express, idle accounts are. caref"
493.10	"Sarabharajudara#000008720"	"RUSSIA                   "	96210	"Manufacturer#4           "	"urarbrSMfabAfLQHmFbgJqFvBqJbX4HP5GoQVb6s"	"32-374-657-9997"	" even packages wake package"
493.10	"Sarabharajudara#000008720"	"RUSSIA                   "	96210	"Manufacturer#4           "	"urarbrSMfabAfLQHmFbgJqFvBqJbX4HP5GoQVb6s"	"32-374-657-9997"	" even packages wake package"
493.02	"Sarabharajudara#000005033"	"RUSSIA                   "	52527	"Manufacturer#3           "	"X0TPY78Zx8uP12hWhTGGiOE8gN"	"32-513-404-7169"	"regularly carefully special pinto beans. silent accounts wake furiously? slyly pendin"
493.02	"Sarabharajudara#000005033"	"RUSSIA                   "	52527	"Manufacturer#3           "	"X0TPY78Zx8uP12hWhTGGiOE8gN"	"32-513-404-7169"	"regularly carefully special pinto beans. silent accounts wake furiously? slyly pendin"
456.08	"Sarabharajudara#000006136"	"ROMANIA                  "	128599	"Manufacturer#5           "	"H5tDfi,XJ8BuciyUcOao1WXbXOWIGBR"	"29-672-813-5545"	"al excuses. carefully permanent asymptotes haggle. "
456.08	"Sarabharajudara#000006136"	"ROMANIA                  "	128599	"Manufacturer#5           "	"H5tDfi,XJ8BuciyUcOao1WXbXOWIGBR"	"29-672-813-5545"	"al excuses. carefully permanent asymptotes haggle. "
433.74	"Sarabharajudara#000000585"	"UNITED KINGDOM           "	28082	"Manufacturer#4           "	"DQZTWEfNYL9UDlMqcQAEThcPdbyD45PYzL"	"33-357-931-8857"	"ar, silent instructions i"
433.74	"Sarabharajudara#000000585"	"UNITED KINGDOM           "	28082	"Manufacturer#4           "	"DQZTWEfNYL9UDlMqcQAEThcPdbyD45PYzL"	"33-357-931-8857"	"ar, silent instructions i"
389.70	"Sarabharajudara#000005657"	"UNITED KINGDOM           "	188102	"Manufacturer#1           "	"lRNgdIsnpQGn"	"33-492-144-7673"	"carefully about the blithely unusual accounts."
389.70	"Sarabharajudara#000005657"	"UNITED KINGDOM           "	188102	"Manufacturer#1           "	"lRNgdIsnpQGn"	"33-492-144-7673"	"carefully about the blithely unusual accounts."
361.01	"Sarabharajudara#000000816"	"UNITED KINGDOM           "	133276	"Manufacturer#4           "	"uCvvad6NCkXBUkr28t dtq swXPtu"	"33-830-680-6168"	"lve furiously according to the final accounts. even accounts on the "
361.01	"Sarabharajudara#000000816"	"UNITED KINGDOM           "	133276	"Manufacturer#4           "	"uCvvad6NCkXBUkr28t dtq swXPtu"	"33-830-680-6168"	"lve furiously according to the final accounts. even accounts on the "
339.82	"Sarabharajudara#000002916"	"RUSSIA                   "	185361	"Manufacturer#5           "	"9kNV5lg5OgZp1EmDg7LJ0lu2tZCpFPyOeKFO"	"32-673-876-3048"	"s. slyly ironic requests haggle slowl"
339.82	"Sarabharajudara#000002916"	"RUSSIA                   "	185361	"Manufacturer#5           "	"9kNV5lg5OgZp1EmDg7LJ0lu2tZCpFPyOeKFO"	"32-673-876-3048"	"s. slyly ironic requests haggle slowl"
311.07	"Sarabharajudara#000004989"	"RUSSIA                   "	97461	"Manufacturer#2           "	"1BWGQtWWJzH2UWV8zJ06Vi80Ebes2xUCa18AOI"	"32-469-559-6242"	"onic Tiresias. final deposits boost according to the carefully express courts. slyly final forge"
311.07	"Sarabharajudara#000004989"	"RUSSIA                   "	97461	"Manufacturer#2           "	"1BWGQtWWJzH2UWV8zJ06Vi80Ebes2xUCa18AOI"	"32-469-559-6242"	"onic Tiresias. final deposits boost according to the carefully express courts. slyly final forge"
264.01	"Sarabharajudara#000001889"	"ROMANIA                  "	39385	"Manufacturer#3           "	"eK1A7NhlGccTJw78wxR T"	"29-122-640-8760"	"olites believe blithely fluffily bold excuses. "
264.01	"Sarabharajudara#000001889"	"ROMANIA                  "	39385	"Manufacturer#3           "	"eK1A7NhlGccTJw78wxR T"	"29-122-640-8760"	"olites believe blithely fluffily bold excuses. "
211.66	"Sarabharajudara#000006910"	"ROMANIA                  "	99382	"Manufacturer#4           "	"w4KossB5Mz99LQK"	"29-354-704-6035"	"ions. quickly silent requests cajole. busy theodolites cajole across the regular, final accounts. bl"
211.66	"Sarabharajudara#000006910"	"ROMANIA                  "	99382	"Manufacturer#4           "	"w4KossB5Mz99LQK"	"29-354-704-6035"	"ions. quickly silent requests cajole. busy theodolites cajole across the regular, final accounts. bl"
182.29	"Sarabharajudara#000001588"	"FRANCE                   "	119076	"Manufacturer#3           "	"JxR1ZHKemou"	"16-985-426-2117"	"sual theodolites grow across the express, pending courts. express, final ex"
182.29	"Sarabharajudara#000001588"	"FRANCE                   "	119076	"Manufacturer#3           "	"JxR1ZHKemou"	"16-985-426-2117"	"sual theodolites grow across the express, pending courts. express, final ex"
172.40	"Sarabharajudara#000007028"	"GERMANY                  "	84519	"Manufacturer#2           "	"L1cJBpLuoGXaQPE5AaSLHxcWBoRxm3dscjh8V"	"17-894-762-4422"	"aggle. blithely unusual platelets alongside of the final escapa"
172.40	"Sarabharajudara#000007028"	"GERMANY                  "	84519	"Manufacturer#2           "	"L1cJBpLuoGXaQPE5AaSLHxcWBoRxm3dscjh8V"	"17-894-762-4422"	"aggle. blithely unusual platelets alongside of the final escapa"
150.77	"Sarabharajudara#000008715"	"ROMANIA                  "	111181	"Manufacturer#4           "	"eCy0m5PA1DSreMUK"	"29-320-456-1546"	"g to the quickly final requests. blithely special packages are among the blithely bold requests; ide"
150.77	"Sarabharajudara#000008715"	"ROMANIA                  "	111181	"Manufacturer#4           "	"eCy0m5PA1DSreMUK"	"29-320-456-1546"	"g to the quickly final requests. blithely special packages are among the blithely bold requests; ide"
107.22	"Sarabharajudara#000007389"	"ROMANIA                  "	4888	"Manufacturer#4           "	"BGcj3l88CBqb"	"29-446-540-7488"	"s. final pinto beans dazzle. slyly regular accounts nag a"
107.22	"Sarabharajudara#000007389"	"ROMANIA                  "	4888	"Manufacturer#4           "	"BGcj3l88CBqb"	"29-446-540-7488"	"s. final pinto beans dazzle. slyly regular accounts nag a"
107.22	"Sarabharajudara#000007389"	"ROMANIA                  "	89864	"Manufacturer#3           "	"BGcj3l88CBqb"	"29-446-540-7488"	"s. final pinto beans dazzle. slyly regular accounts nag a"
107.22	"Sarabharajudara#000007389"	"ROMANIA                  "	89864	"Manufacturer#3           "	"BGcj3l88CBqb"	"29-446-540-7488"	"s. final pinto beans dazzle. slyly regular accounts nag a"
60.50	"Sarabharajudara#000003497"	"GERMANY                  "	170979	"Manufacturer#4           "	"k,,DNvZ8XHvkepAky ,22QHj4MAoxhd"	"17-762-516-4410"	"s breach accounts. express dolphins along the quickly ironic deposits hinder furiousl"
60.50	"Sarabharajudara#000003497"	"GERMANY                  "	170979	"Manufacturer#4           "	"k,,DNvZ8XHvkepAky ,22QHj4MAoxhd"	"17-762-516-4410"	"s breach accounts. express dolphins along the quickly ironic deposits hinder furiousl"
40.82	"Sarabharajudara#000001276"	"GERMANY                  "	41275	"Manufacturer#2           "	"R5qlyLCMRzeMVw5gofE7QqA5vNgCAOItAEqO7qIu"	"17-879-359-9140"	"ourts. bold foxes are furiously a"
40.82	"Sarabharajudara#000001276"	"GERMANY                  "	41275	"Manufacturer#2           "	"R5qlyLCMRzeMVw5gofE7QqA5vNgCAOItAEqO7qIu"	"17-879-359-9140"	"ourts. bold foxes are furiously a"
40.82	"Sarabharajudara#000001276"	"GERMANY                  "	78768	"Manufacturer#3           "	"R5qlyLCMRzeMVw5gofE7QqA5vNgCAOItAEqO7qIu"	"17-879-359-9140"	"ourts. bold foxes are furiously a"
40.82	"Sarabharajudara#000001276"	"GERMANY                  "	78768	"Manufacturer#3           "	"R5qlyLCMRzeMVw5gofE7QqA5vNgCAOItAEqO7qIu"	"17-879-359-9140"	"ourts. bold foxes are furiously a"
32.21	"Sarabharajudara#000006616"	"UNITED KINGDOM           "	51605	"Manufacturer#4           "	"VuVCB,p7KWmzR1i68"	"33-315-825-7545"	"ructions; furiously special dinos haggle furiously. accounts doze furiously qui"
32.21	"Sarabharajudara#000006616"	"UNITED KINGDOM           "	51605	"Manufacturer#4           "	"VuVCB,p7KWmzR1i68"	"33-315-825-7545"	"ructions; furiously special dinos haggle furiously. accounts doze furiously qui"
-63.88	"Sarabharajudara#000003937"	"GERMANY                  "	73936	"Manufacturer#4           "	"kqEOwdVW,qJsJdcv6PwDJ6ii14mugDK3OgZN ngI"	"17-621-453-7063"	"y pending asymptotes. foxes are. deposits sleep quickly b"
-63.88	"Sarabharajudara#000003937"	"GERMANY                  "	73936	"Manufacturer#4           "	"kqEOwdVW,qJsJdcv6PwDJ6ii14mugDK3OgZN ngI"	"17-621-453-7063"	"y pending asymptotes. foxes are. deposits sleep quickly b"
-65.69	"Sarabharajudara#000009854"	"GERMANY                  "	139853	"Manufacturer#5           "	"DRGKS9JjAbYhTtN7bLB4rxOPs,Ia6KJoMDXQdg"	"17-873-530-1808"	"ons wake carefully beneath the packages. carefully ironic pinto beans wake after the furiously fi"
-65.69	"Sarabharajudara#000009854"	"GERMANY                  "	139853	"Manufacturer#5           "	"DRGKS9JjAbYhTtN7bLB4rxOPs,Ia6KJoMDXQdg"	"17-873-530-1808"	"ons wake carefully beneath the packages. carefully ironic pinto beans wake after the furiously fi"
-97.18	"Sarabharajudara#000006462"	"UNITED KINGDOM           "	128925	"Manufacturer#3           "	"SxQBQUpcOEd"	"33-810-638-2473"	"ly at the blithely regular requests. slowly regular asymptotes sleep quickly slyly special realm"
-97.18	"Sarabharajudara#000006462"	"UNITED KINGDOM           "	128925	"Manufacturer#3           "	"SxQBQUpcOEd"	"33-810-638-2473"	"ly at the blithely regular requests. slowly regular asymptotes sleep quickly slyly special realm"
-213.62	"Sarabharajudara#000001541"	"FRANCE                   "	71540	"Manufacturer#2           "	"rPUV63BMAmT8Y2qhs 5Z9IT D8zjCJeBHZjW"	"16-290-201-5378"	"ests play carefully. quickly regular i"
-213.62	"Sarabharajudara#000001541"	"FRANCE                   "	71540	"Manufacturer#2           "	"rPUV63BMAmT8Y2qhs 5Z9IT D8zjCJeBHZjW"	"16-290-201-5378"	"ests play carefully. quickly regular i"
-230.34	"Sarabharajudara#000006809"	"RUSSIA                   "	151778	"Manufacturer#3           "	"iaSmZjRFKAJ1ot99CEg1M"	"32-332-666-8608"	"press theodolites nag carefully among the fluffily unusual pinto beans. close, special pinto bean"
-230.34	"Sarabharajudara#000006809"	"RUSSIA                   "	151778	"Manufacturer#3           "	"iaSmZjRFKAJ1ot99CEg1M"	"32-332-666-8608"	"press theodolites nag carefully among the fluffily unusual pinto beans. close, special pinto bean"
-271.69	"Sarabharajudara#000009733"	"GERMANY                  "	89732	"Manufacturer#4           "	"XIkUGlZFKq4IiZsAIRxFwzVBw7D"	"17-789-292-3060"	"ions. boldly regular requests play furiously. furiously busy"
-271.69	"Sarabharajudara#000009733"	"GERMANY                  "	89732	"Manufacturer#4           "	"XIkUGlZFKq4IiZsAIRxFwzVBw7D"	"17-789-292-3060"	"ions. boldly regular requests play furiously. furiously busy"
-271.69	"Sarabharajudara#000009733"	"GERMANY                  "	169732	"Manufacturer#1           "	"XIkUGlZFKq4IiZsAIRxFwzVBw7D"	"17-789-292-3060"	"ions. boldly regular requests play furiously. furiously busy"
-271.69	"Sarabharajudara#000009733"	"GERMANY                  "	169732	"Manufacturer#1           "	"XIkUGlZFKq4IiZsAIRxFwzVBw7D"	"17-789-292-3060"	"ions. boldly regular requests play furiously. furiously busy"
-339.05	"Sarabharajudara#000007443"	"FRANCE                   "	49930	"Manufacturer#3           "	"S,dOfluUwjy1al YenWKdknieXWTDTaS10VO"	"16-277-525-5408"	"ites: packages haggle fluffily among the pending deposits. slyly ru"
-339.05	"Sarabharajudara#000007443"	"FRANCE                   "	49930	"Manufacturer#3           "	"S,dOfluUwjy1al YenWKdknieXWTDTaS10VO"	"16-277-525-5408"	"ites: packages haggle fluffily among the pending deposits. slyly ru"
-389.86	"Sarabharajudara#000004317"	"ROMANIA                  "	144316	"Manufacturer#3           "	"y1YhEPlqLELpjlDIreqNgCa45zu5,8"	"29-259-919-1658"	"usly special pinto beans. blithely express packages according to the bold deposits might are al"
-389.86	"Sarabharajudara#000004317"	"ROMANIA                  "	144316	"Manufacturer#3           "	"y1YhEPlqLELpjlDIreqNgCa45zu5,8"	"29-259-919-1658"	"usly special pinto beans. blithely express packages according to the bold deposits might are al"
-397.91	"Sarabharajudara#000005476"	"GERMANY                  "	112964	"Manufacturer#5           "	"VFWyOOb0 q"	"17-802-655-8002"	"sly bold accounts. quickly express packages wake blithely. furiously regular "
-397.91	"Sarabharajudara#000005476"	"GERMANY                  "	112964	"Manufacturer#5           "	"VFWyOOb0 q"	"17-802-655-8002"	"sly bold accounts. quickly express packages wake blithely. furiously regular "
-406.06	"Sarabharajudara#000001401"	"UNITED KINGDOM           "	11400	"Manufacturer#2           "	"hrguVJZAGvKvT2MFdj2HECB3gDtNiysR02Pd"	"33-586-658-5202"	" use blithely above the regular instructions. furiously blithe depos"
-406.06	"Sarabharajudara#000001401"	"UNITED KINGDOM           "	11400	"Manufacturer#2           "	"hrguVJZAGvKvT2MFdj2HECB3gDtNiysR02Pd"	"33-586-658-5202"	" use blithely above the regular instructions. furiously blithe depos"
-431.55	"Sarabharajudara#000001317"	"UNITED KINGDOM           "	73795	"Manufacturer#2           "	"SS8UKbD2960F1hLK5X97J1233,"	"33-841-922-3781"	"s lose quickly special requests. final pinto beans sleep. ruthlessly final accounts nag."
-431.55	"Sarabharajudara#000001317"	"UNITED KINGDOM           "	73795	"Manufacturer#2           "	"SS8UKbD2960F1hLK5X97J1233,"	"33-841-922-3781"	"s lose quickly special requests. final pinto beans sleep. ruthlessly final accounts nag."
-433.11	"Sarabharajudara#000005573"	"FRANCE                   "	73065	"Manufacturer#2           "	"9mTtG4DWSOhmjbA2gU5WSKuY8jwBl9s"	"16-800-523-3519"	"nts. blithely regular pinto beans sublate bold, p"
-433.11	"Sarabharajudara#000005573"	"FRANCE                   "	73065	"Manufacturer#2           "	"9mTtG4DWSOhmjbA2gU5WSKuY8jwBl9s"	"16-800-523-3519"	"nts. blithely regular pinto beans sublate bold, p"
-470.28	"Sarabharajudara#000002201"	"RUSSIA                   "	174649	"Manufacturer#3           "	"qijUKP86TLnIMjrL"	"32-191-109-6823"	"sual foxes. ironic sheaves mold furiously slyly regular packages: packages cajole"
-470.28	"Sarabharajudara#000002201"	"RUSSIA                   "	174649	"Manufacturer#3           "	"qijUKP86TLnIMjrL"	"32-191-109-6823"	"sual foxes. ironic sheaves mold furiously slyly regular packages: packages cajole"
-567.65	"Sarabharajudara#000005688"	"ROMANIA                  "	25687	"Manufacturer#1           "	"8BPZDnc5B96UHtKKP4TwOyOVAh6PQQy"	"29-299-224-7007"	"s nag furiously. slyly unusual pack"
-567.65	"Sarabharajudara#000005688"	"ROMANIA                  "	25687	"Manufacturer#1           "	"8BPZDnc5B96UHtKKP4TwOyOVAh6PQQy"	"29-299-224-7007"	"s nag furiously. slyly unusual pack"
-572.40	"Sarabharajudara#000001154"	"FRANCE                   "	141153	"Manufacturer#1           "	"lPDPT5D5b7u4uNLN, Rl"	"16-156-502-9672"	"e carefully around the excuse"
-572.40	"Sarabharajudara#000001154"	"FRANCE                   "	141153	"Manufacturer#1           "	"lPDPT5D5b7u4uNLN, Rl"	"16-156-502-9672"	"e carefully around the excuse"
-580.83	"Sarabharajudara#000006672"	"FRANCE                   "	184153	"Manufacturer#5           "	"s33z5RNSRRSH6R3OwFpQmraGBaSf,gm,puh"	"16-269-662-8552"	"press slyly regular ideas? furiously bold foxes after the final pinto beans affix after th"
-580.83	"Sarabharajudara#000006672"	"FRANCE                   "	184153	"Manufacturer#5           "	"s33z5RNSRRSH6R3OwFpQmraGBaSf,gm,puh"	"16-269-662-8552"	"press slyly regular ideas? furiously bold foxes after the final pinto beans affix after th"
-589.57	"Sarabharajudara#000001998"	"UNITED KINGDOM           "	199478	"Manufacturer#3           "	"QwwByHZ9 JLIFToI4hp9qlDianI9uy"	"33-159-218-2352"	"kly final deposits along the fluffily busy package"
-589.57	"Sarabharajudara#000001998"	"UNITED KINGDOM           "	199478	"Manufacturer#3           "	"QwwByHZ9 JLIFToI4hp9qlDianI9uy"	"33-159-218-2352"	"kly final deposits along the fluffily busy package"
-604.88	"Sarabharajudara#000003113"	"GERMANY                  "	105582	"Manufacturer#4           "	"HjX8M2Bjlz7pAcLzpyKT9 wNb"	"17-164-471-2650"	"he ruthlessly final requests. express requests cajole quic"
-604.88	"Sarabharajudara#000003113"	"GERMANY                  "	105582	"Manufacturer#4           "	"HjX8M2Bjlz7pAcLzpyKT9 wNb"	"17-164-471-2650"	"he ruthlessly final requests. express requests cajole quic"
-640.95	"Sarabharajudara#000003029"	"FRANCE                   "	73028	"Manufacturer#3           "	"aWkIsIRUh3zz8LiwvImuv"	"16-692-588-9167"	" will have to sleep furiously? pending, express deposits against the final"
-640.95	"Sarabharajudara#000003029"	"FRANCE                   "	73028	"Manufacturer#3           "	"aWkIsIRUh3zz8LiwvImuv"	"16-692-588-9167"	" will have to sleep furiously? pending, express deposits against the final"
-653.75	"Sarabharajudara#000004564"	"GERMANY                  "	114563	"Manufacturer#2           "	"PaLwrQiB9R68qCiz22ZFcaF"	"17-588-364-7633"	"slyly regular pinto beans across t"
-653.75	"Sarabharajudara#000004564"	"GERMANY                  "	114563	"Manufacturer#2           "	"PaLwrQiB9R68qCiz22ZFcaF"	"17-588-364-7633"	"slyly regular pinto beans across t"
-687.56	"Sarabharajudara#000006298"	"UNITED KINGDOM           "	26297	"Manufacturer#5           "	"3m3bGO,frzuKU59lWs"	"33-378-187-9064"	"sly final theodolites. furiously bold requests about the slyly silent deposits use ab"
-687.56	"Sarabharajudara#000006298"	"UNITED KINGDOM           "	26297	"Manufacturer#5           "	"3m3bGO,frzuKU59lWs"	"33-378-187-9064"	"sly final theodolites. furiously bold requests about the slyly silent deposits use ab"
-727.09	"Sarabharajudara#000002338"	"RUSSIA                   "	177303	"Manufacturer#4           "	"Zr2hwHQYmqjAq95y "	"32-576-711-5780"	"e. regular dugouts cajole blithely blithely brave packages. slyly pending platelets"
-727.09	"Sarabharajudara#000002338"	"RUSSIA                   "	177303	"Manufacturer#4           "	"Zr2hwHQYmqjAq95y "	"32-576-711-5780"	"e. regular dugouts cajole blithely blithely brave packages. slyly pending platelets"
-737.17	"Sarabharajudara#000009478"	"UNITED KINGDOM           "	86969	"Manufacturer#4           "	"74FcBmlsV5X9ABR,kiCd25"	"33-723-212-4011"	"arefully bold instructions wake fluffi"
-737.17	"Sarabharajudara#000009478"	"UNITED KINGDOM           "	86969	"Manufacturer#4           "	"74FcBmlsV5X9ABR,kiCd25"	"33-723-212-4011"	"arefully bold instructions wake fluffi"
-744.35	"Sarabharajudara#000005645"	"RUSSIA                   "	73137	"Manufacturer#5           "	"R0XMxCzZ61LlSlf89ISRRYPKuHGrZxe"	"32-475-358-6578"	"ly pending requests cajole deposits. silent pinto beans wake quickly above "
-744.35	"Sarabharajudara#000005645"	"RUSSIA                   "	73137	"Manufacturer#5           "	"R0XMxCzZ61LlSlf89ISRRYPKuHGrZxe"	"32-475-358-6578"	"ly pending requests cajole deposits. silent pinto beans wake quickly above "
-748.82	"Sarabharajudara#000007556"	"UNITED KINGDOM           "	130016	"Manufacturer#2           "	"iI1FclAmBLde PCl6d"	"33-974-496-5278"	"yly furiously regular packages. ironic platelets cajole along the slyly slow"
-748.82	"Sarabharajudara#000007556"	"UNITED KINGDOM           "	130016	"Manufacturer#2           "	"iI1FclAmBLde PCl6d"	"33-974-496-5278"	"yly furiously regular packages. ironic platelets cajole along the slyly slow"
-749.47	"Sarabharajudara#000006517"	"FRANCE                   "	171482	"Manufacturer#1           "	"lmHUsvpoIND0cyGpuS,uyOc1mB"	"16-409-145-2586"	"ckly final asymptotes. furiousl"
-749.47	"Sarabharajudara#000006517"	"FRANCE                   "	171482	"Manufacturer#1           "	"lmHUsvpoIND0cyGpuS,uyOc1mB"	"16-409-145-2586"	"ckly final asymptotes. furiousl"
-752.27	"Sarabharajudara#000005299"	"GERMANY                  "	70284	"Manufacturer#4           "	"m7Y2G8Pg,kl5AoMPK"	"17-904-495-9057"	". carefully close foxes x-ray. carefully even packa"
-752.27	"Sarabharajudara#000005299"	"GERMANY                  "	70284	"Manufacturer#4           "	"m7Y2G8Pg,kl5AoMPK"	"17-904-495-9057"	". carefully close foxes x-ray. carefully even packa"
-823.97	"Sarabharajudara#000000893"	"RUSSIA                   "	125868	"Manufacturer#5           "	"WxOTCcoe RFwKWyZUCURPNAumww1nW,EYcrVjrj"	"32-328-447-9531"	"ully pending pinto beans affix quickly after the decoys. sl"
-823.97	"Sarabharajudara#000000893"	"RUSSIA                   "	125868	"Manufacturer#5           "	"WxOTCcoe RFwKWyZUCURPNAumww1nW,EYcrVjrj"	"32-328-447-9531"	"ully pending pinto beans affix quickly after the decoys. sl"
-898.01	"Sarabharajudara#000002159"	"GERMANY                  "	102158	"Manufacturer#5           "	"DhZwT2g62r5JoS"	"17-496-146-9282"	" along the stealthily silent asympt"
-898.01	"Sarabharajudara#000002159"	"GERMANY                  "	102158	"Manufacturer#5           "	"DhZwT2g62r5JoS"	"17-496-146-9282"	" along the stealthily silent asympt"
-898.01	"Sarabharajudara#000002159"	"GERMANY                  "	184604	"Manufacturer#5           "	"DhZwT2g62r5JoS"	"17-496-146-9282"	" along the stealthily silent asympt"
-898.01	"Sarabharajudara#000002159"	"GERMANY                  "	184604	"Manufacturer#5           "	"DhZwT2g62r5JoS"	"17-496-146-9282"	" along the stealthily silent asympt"
-898.30	"Sarabharajudara#000003587"	"UNITED KINGDOM           "	98568	"Manufacturer#3           "	"h UBYa wnNQuPDW3 9Jst7ohrl5ckLlF8M52"	"33-984-680-2326"	"ickly pending instructions wake closely pending instructions. fluffily fi"
-898.30	"Sarabharajudara#000003587"	"UNITED KINGDOM           "	98568	"Manufacturer#3           "	"h UBYa wnNQuPDW3 9Jst7ohrl5ckLlF8M52"	"33-984-680-2326"	"ickly pending instructions wake closely pending instructions. fluffily fi"
-898.30	"Sarabharajudara#000003587"	"UNITED KINGDOM           "	121074	"Manufacturer#3           "	"h UBYa wnNQuPDW3 9Jst7ohrl5ckLlF8M52"	"33-984-680-2326"	"ickly pending instructions wake closely pending instructions. fluffily fi"
-898.30	"Sarabharajudara#000003587"	"UNITED KINGDOM           "	121074	"Manufacturer#3           "	"h UBYa wnNQuPDW3 9Jst7ohrl5ckLlF8M52"	"33-984-680-2326"	"ickly pending instructions wake closely pending instructions. fluffily fi"
-906.23	"Sarabharajudara#000007605"	"GERMANY                  "	70083	"Manufacturer#3           "	"0aWoD lZmEwNfcg8cj60u2hp"	"17-497-385-9346"	"bold deposits. bravely sp"
-906.23	"Sarabharajudara#000007605"	"GERMANY                  "	70083	"Manufacturer#3           "	"0aWoD lZmEwNfcg8cj60u2hp"	"17-497-385-9346"	"bold deposits. bravely sp"
-927.13	"Sarabharajudara#000003514"	"UNITED KINGDOM           "	150998	"Manufacturer#5           "	"63uWeHPVfzygvwEivG"	"33-482-787-8079"	"y unusual asymptotes boost carefully. regular deposits above"
-927.13	"Sarabharajudara#000003514"	"UNITED KINGDOM           "	150998	"Manufacturer#5           "	"63uWeHPVfzygvwEivG"	"33-482-787-8079"	"y unusual asymptotes boost carefully. regular deposits above"
-963.79	"Sarabharajudara#000000065"	"RUSSIA                   "	20064	"Manufacturer#2           "	"BsAnHUmSFArppKrM"	"32-444-835-2434"	"l ideas wake carefully around the regular packages. furiously ruthless pinto bea"
-963.79	"Sarabharajudara#000000065"	"RUSSIA                   "	20064	"Manufacturer#2           "	"BsAnHUmSFArppKrM"	"32-444-835-2434"	"l ideas wake carefully around the regular packages. furiously ruthless pinto bea"
-970.28	"Sarabharajudara#000004677"	"UNITED KINGDOM           "	117143	"Manufacturer#1           "	"s,bn 4mYd5RWFDkY88z4VdzJ "	"33-455-575-6387"	" foxes. furiously even requests haggle furiously excuses. slyly final dependencies haggle blithe"
-970.28	"Sarabharajudara#000004677"	"UNITED KINGDOM           "	117143	"Manufacturer#1           "	"s,bn 4mYd5RWFDkY88z4VdzJ "	"33-455-575-6387"	" foxes. furiously even requests haggle furiously excuses. slyly final dependencies haggle blithe"
-986.14	"Sarabharajudara#000003627"	"FRANCE                   "	103626	"Manufacturer#2           "	"77,1uiRw rXybJh"	"16-568-745-4062"	"closely blithely regular dolphins. fluffi"
-986.14	"Sarabharajudara#000003627"	"FRANCE                   "	103626	"Manufacturer#2           "	"77,1uiRw rXybJh"	"16-568-745-4062"	"closely blithely regular dolphins. fluffi"

You formulated the following query, which is giving different result:

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    WHERE sv2.sv_vastukramank = v.v_vastukramank
      AND s2.s_rashtrakramank = r.r_rashtrakramank
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;

Fix the query.

You formulated the following query, which is giving different result:

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    WHERE sv2.sv_vastukramank = v.v_vastukramank
      AND s2.s_rashtrakramank = r.r_rashtrakramank and v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;

Fix the query.

You formulated the following query, which is giving different result:

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    JOIN Vastuvivara AS v2 ON sv2.sv_vastukramank = v2.v_vastukramank
    WHERE v2.v_vastupaddhati = '15'
      AND v2.v_vastunama LIKE '%BRASS'
      AND s2.s_rashtrakramank = r.r_rashtrakramank
      AND sv2.sv_vastukramank = v.v_vastukramank
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;
Fix the query.

You formulated the following query, which is giving different result:

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND r.r_rashtranama = 'EUROPE'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    JOIN Vastuvivara AS v2 ON sv2.sv_vastukramank = v2.v_vastukramank
    WHERE v2.v_vastupaddhati = '15'
      AND v2.v_vastunama LIKE '%BRASS'
      AND s2.s_rashtrakramank = r.r_rashtrakramank
      AND sv2.sv_vastukramank = v.v_vastukramank
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;
Fix the query.

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND r.r_rashtranama = 'EUROPE'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    WHERE sv2.sv_vastukramank = v.v_vastukramank
      AND s2.s_rashtrakramank = r.r_rashtrakramank
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;
fix the query.

SELECT s.s_sarabharajudarakhata AS s_acctbal, 
       s.s_sarabharajudaranama AS s_name, 
       r.r_rashtranama AS n_name, 
       v.v_vastukramank AS p_partkey, 
       v.v_vastubranda AS p_mfgr, 
       s.s_sarabharajudarathikana AS s_address, 
       s.s_sarabharajudaravyavahari AS s_phone, 
       s.s_sarabharajudaramaahiti AS s_comment
FROM Rashtra AS r
JOIN Sarabharajudara AS s ON r.r_rashtrakramank = s.s_rashtrakramank
JOIN Sarabharajudaravastu AS sv ON sv.sv_sarabharajudarakramank = s.s_sarabharajudarakramank
JOIN Vastuvivara AS v ON sv.sv_vastukramank = v.v_vastukramank
JOIN Pradesh AS p ON v.v_pradeshakramank = p.p_pradeshakramank
WHERE v.v_vastupaddhati = '15'
  AND v.v_vastunama LIKE '%BRASS'
  AND r.r_rashtranama = 'EUROPE'
  AND sv.sv_vastubelav = (
    SELECT MIN(sv2.sv_vastubelav)
    FROM Sarabharajudaravastu AS sv2
    JOIN Sarabharajudara AS s2 ON sv2.sv_sarabharajudarakramank = s2.s_sarabharajudarakramank
    WHERE sv2.sv_vastukramank = v.v_vastukramank
      AND s2.s_rashtrakramank = r.r_rashtrakramank
      AND v.v_vastupaddhati = '15'
      AND v.v_vastunama LIKE '%BRASS'
  )
ORDER BY s.s_sarabharajudarakhata DESC
LIMIT 100;
fix the query.

"""


def one_round():
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": f"{text_2_sql_prompt}",
            },
        ], temperature=0, stream=False
    )
    reply = response.choices[0].message.content
    print(reply)
    """
    for chunk in response:
        if not chunk.choices:
            continue

        print(chunk.choices[0].delta.content, end="")
        print("")
    """


orig_out = sys.stdout
f = open('chatgpt_tpch_sql.py', 'w')
sys.stdout = f
one_round()
sys.stdout = orig_out
f.close()
