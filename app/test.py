import util

status = """version : 8622567/24 8622567 secure
hostname: LazyPurple's Silly Server #1
udp/ip  : 192.223.26.238:27015
steamid : [G:1:2391404] (85568392922430828)
account : not logged in  (No account specified)
tags    : alltalk,custom,friendly,increased_maxplayers,lazypurple,minecraft,nocrits,norespawntime,pootis,respawntimes,silly
map     : ctf_free2fort at: 0 x, 0 y, 0 z
players : 29 humans, 0 bots (32 max)
edicts  : 1289 used of 2048 max
#    112 "Medineer™"       [U:1:57299052]      35:56      106    0 active
# userid name                uniqueid            connected ping loss state
#    134 "Random_Mii"        [U:1:1542043877]    01:34       79    0 active
#     84 "The Panning"       [U:1:332128397]     59:49      295    0 active
#     69 "Grandpa"           [U:1:84784636]       1:27:34    87    0 active
#    124 "Palpe la pulpe du Poulpe" [U:1:101454970] 22:56   148    0 active
#    131 "Cap'n Cringebeard" [U:1:463393799]     11:23       85    0 active
#    107 "pug"               [U:1:226134902]     40:19       75    0 active
#     86 "Gribbinski"        [U:1:958831264]     57:41      103    0 active
#     77 "Icy Âme ❄"      [U:1:11113514]       1:13:01   103    0 active
#    104 "Crepe"             [U:1:1112127866]    41:34       72    0 active
#     87 "thing"             [U:1:1161059698]    56:53      124    0 active
#     65 "7-Up X Sierra mist" [U:1:1582581898]    1:39:57   306    0 active
#    121 "Hyperthread"       [U:1:167658680]     28:16      106    0 active
#    106 "TM CHRS LR"        [U:1:327059956]     40:40       98    0 active
#    122 "111112oo"          [U:1:91550113]      27:13      281    0 active
#     19 "UmbreonRogue"      [U:1:301805850]      2:35:23    86    0 active
#    118 "HIYAAAAA"          [U:1:119916553]     31:17      113    0 active
#     99 "ZippLeafeon"       [U:1:83521152]      45:06       99    0 active
#    132 "assu!"             [U:1:95269734]      06:31       78    0 active
#    120 "asko"              [U:1:1121333420]    29:17      132    0 active
#     23 "Pollyx0123"        [U:1:204666582]      2:34:55   136    0 active
#     24 "Masonator"         [U:1:449416302]      2:34:52   111    0 active
#     25 "Lee Harvey Oswald" [U:1:1507639960]     2:34:31    90    0 active
#    135 "dungasteam51"      [U:1:1582098704]    00:23      199   43 spawning
#     67 "distracted_pootisman" [U:1:120403971]   1:33:46    91    0 active
#    127 "spookifier"        [U:1:346127822]     18:01       91    0 active
#     31 "★NL★ Kesova!"  [U:1:1020715231]     2:28:46    99    0 active
#    129 "DeezYipiiPlayzz"   [U:1:1298446235]    16:55      299    0 active
#    133 "Kiwi"              [U:1:85706123]      04:46      135    0 active

"""

util.filter_status(status)