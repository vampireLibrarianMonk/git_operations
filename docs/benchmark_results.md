# Model Benchmark Results

Last updated: 2026-06-17 09:29
Total trials: 525

## Leaderboard

| Model                | Trials | Quality | Avg Cost  | Avg Latency |
| -------------------- | ------ | ------- | --------- | ----------- |
| Llama 3.1 70B        | 6      | 100%    | $0.003154 | 11942ms     |
| Llama 3.3 70B        | 27     | 100%    | $0.010433 | 4219ms      |
| Claude Opus 4.1      | 27     | 99%     | $0.233756 | 21667ms     |
| Llama 4 Scout 17B    | 27     | 98%     | $0.002474 | 6192ms      |
| Claude Sonnet 4.6    | 27     | 98%     | $0.049962 | 12720ms     |
| Claude Sonnet 4.5    | 27     | 98%     | $0.050785 | 14280ms     |
| Devstral 2 123B      | 19     | 97%     | $0.006680 | 17929ms     |
| DeepSeek R1          | 27     | 97%     | $0.020376 | 10851ms     |
| DeepSeek V3.2        | 27     | 97%     | $0.007927 | 9004ms      |
| Magistral Small      | 27     | 96%     | $0.007601 | 10347ms     |
| Llama 4 Maverick 17B | 27     | 96%     | $0.002447 | 2328ms      |
| Nova Lite            | 27     | 95%     | $0.000945 | 6189ms      |
| Mistral Large 3      | 27     | 95%     | $0.030297 | 6409ms      |
| Nova Micro           | 27     | 91%     | $0.000530 | 2777ms      |
| Ministral 14B        | 27     | 88%     | $0.002896 | 4640ms      |
| Claude 3 Haiku       | 27     | 87%     | $0.004156 | 6160ms      |
| Claude Haiku 4.5     | 27     | 84%     | $0.016791 | 6662ms      |
| Nova Pro             | 24     | 83%     | $0.010623 | 7912ms      |
| Ministral 3B         | 27     | 80%     | $0.000587 | 9211ms      |
| Ministral 8B         | 26     | 77%     | $0.001361 | 6062ms      |
| Nova 2 Lite          | 18     | 76%     | $0.000947 | 2839ms      |

**Recommended: Llama 3.3 70B** (`us.meta.llama3-3-70b-instruct-v1:0`)

## Trial Details

| Model                | Repo              | Commit         | Diff Size | Valid | Latency | Cost      |
| -------------------- | ----------------- | -------------- | --------- | ----- | ------- | --------- |
| Ministral 3B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✗     | 730ms   | $0.000065 |
| Nova Micro           | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 969ms   | $0.000061 |
| Llama 4 Scout 17B    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1071ms  | $0.000275 |
| Ministral 8B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1127ms  | $0.000169 |
| Nova Lite            | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1239ms  | $0.000117 |
| Claude 3 Haiku       | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1713ms  | $0.000554 |
| Llama 4 Maverick 17B | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 794ms   | $0.000277 |
| Ministral 14B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 857ms   | $0.000324 |
| Nova Pro             | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1749ms  | $0.001559 |
| Claude Haiku 4.5     | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2141ms  | $0.002218 |
| Llama 3.3 70B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 970ms   | $0.001150 |
| Mistral Large 3      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1044ms  | $0.003683 |
| Devstral 2 123B      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2429ms  | $0.001051 |
| DeepSeek V3.2        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2155ms  | $0.000960 |
| Claude Sonnet 4.5    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3756ms  | $0.006851 |
| Magistral Small      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1651ms  | $0.000940 |
| Claude Sonnet 4.6    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 4257ms  | $0.006896 |
| Nova Micro           | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 892ms   | $0.000072 |
| Nova Lite            | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1017ms  | $0.000116 |
| Ministral 3B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 768ms   | $0.000069 |
| Ministral 8B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1223ms  | $0.000180 |
| Llama 3.1 70B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3302ms  | $0.001184 |
| Llama 4 Scout 17B    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1308ms  | $0.000290 |
| DeepSeek R1          | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 4694ms  | $0.002631 |
| Nova Pro             | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1102ms  | $0.001645 |
| Claude 3 Haiku       | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2735ms  | $0.000677 |
| Ministral 14B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1225ms  | $0.000355 |
| Llama 4 Maverick 17B | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1178ms  | $0.000291 |
| Claude Haiku 4.5     | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2572ms  | $0.002468 |
| Llama 3.3 70B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1132ms  | $0.001226 |
| Devstral 2 123B      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2056ms  | $0.001009 |
| DeepSeek V3.2        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2380ms  | $0.001064 |
| Claude Opus 4.1      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 10413ms | $0.031778 |
| Mistral Large 3      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1122ms  | $0.003995 |
| Claude Sonnet 4.5    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 4625ms  | $0.007021 |
| Magistral Small      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2099ms  | $0.001031 |
| Nova Micro           | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 616ms   | $0.000062 |
| Claude Sonnet 4.6    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 4494ms  | $0.007388 |
| Nova Lite            | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1090ms  | $0.000117 |
| Ministral 3B         | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 589ms   | $0.000068 |
| Llama 4 Scout 17B    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 843ms   | $0.000279 |
| Ministral 8B         | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 958ms   | $0.000173 |
| Claude 3 Haiku       | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1585ms  | $0.000549 |
| Llama 3.1 70B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 3419ms  | $0.001221 |
| Ministral 14B        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 946ms   | $0.000339 |
| Llama 4 Maverick 17B | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 824ms   | $0.000281 |
| Nova Pro             | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 975ms   | $0.001530 |
| DeepSeek R1          | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 5259ms  | $0.002937 |
| Llama 3.3 70B        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1112ms  | $0.001214 |
| Devstral 2 123B      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1546ms  | $0.000978 |
| Claude Haiku 4.5     | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 3012ms  | $0.002659 |
| DeepSeek V3.2        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 2042ms  | $0.000985 |
| Mistral Large 3      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 917ms   | $0.003813 |
| Claude Sonnet 4.5    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 4576ms  | $0.007160 |
| Magistral Small      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1120ms  | $0.000924 |
| Claude Opus 4.1      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 12844ms | $0.034222 |
| Claude Sonnet 4.6    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 4696ms  | $0.007025 |
| Nova Micro           | document_search   | `564670dcb6b9` | 4,720     | ✓     | 867ms   | $0.000084 |
| Nova Lite            | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1226ms  | $0.000159 |
| Ministral 3B         | document_search   | `564670dcb6b9` | 4,720     | ✗     | 564ms   | $0.000093 |
| Llama 3.1 70B        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 2930ms  | $0.001200 |
| Llama 4 Scout 17B    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1227ms  | $0.000403 |
| DeepSeek R1          | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 4687ms  | $0.002828 |
| Ministral 8B         | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2050ms  | $0.000249 |
| Nova Pro             | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1209ms  | $0.002080 |
| Ministral 14B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1633ms  | $0.000508 |
| Llama 4 Maverick 17B | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1156ms  | $0.000406 |
| Claude 3 Haiku       | document_search   | `564670dcb6b9` | 4,720     | ✓     | 4249ms  | $0.000841 |
| Claude Haiku 4.5     | document_search   | `564670dcb6b9` | 4,720     | ✓     | 3587ms  | $0.003531 |
| Llama 3.3 70B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1440ms  | $0.001718 |
| Claude Opus 4.1      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 10399ms | $0.030514 |
| DeepSeek V3.2        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2260ms  | $0.001402 |
| Devstral 2 123B      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2816ms  | $0.001530 |
| Mistral Large 3      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1201ms  | $0.005346 |
| Magistral Small      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2003ms  | $0.001383 |
| Claude Sonnet 4.5    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 5255ms  | $0.010201 |
| DeepSeek R1          | document_search   | `564670dcb6b9` | 4,720     | ✓     | 4370ms  | $0.003970 |
| Claude Sonnet 4.6    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 6858ms  | $0.010973 |
| Llama 3.1 70B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 4193ms  | $0.001706 |
| Nova Lite            | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 5361ms  | $0.002246 |
| Ministral 3B         | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 2491ms  | $0.001441 |
| Claude Opus 4.1      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 11265ms | $0.043804 |
| Ministral 8B         | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 4474ms  | $0.003618 |
| Llama 4 Scout 17B    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 4742ms  | $0.006124 |
| Ministral 14B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 4964ms  | $0.007200 |
| Nova Micro           | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 14347ms | $0.001533 |
| Llama 4 Maverick 17B | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3844ms  | $0.006133 |
| Claude Haiku 4.5     | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 16519ms | $0.041658 |
| Claude 3 Haiku       | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 20785ms | $0.011435 |
| Llama 3.3 70B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 6318ms  | $0.026099 |
| DeepSeek V3.2        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 13894ms | $0.018813 |
| Mistral Large 3      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 11553ms | $0.075172 |
| Claude Sonnet 4.5    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 38824ms | $0.127705 |
| Claude Opus 4.1      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 26971ms | $0.579217 |
| Nova Pro             | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 57107ms | $0.039105 |
| Claude Sonnet 4.6    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 36416ms | $0.127060 |
| Magistral Small      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 17669ms | $0.019459 |
| Nova Micro           | document_search   | `b35551a0f602` | 19,894    | ✓     | 734ms   | $0.000220 |
| DeepSeek R1          | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 14414ms | $0.050233 |
| Nova Lite            | document_search   | `b35551a0f602` | 19,894    | ✓     | 2124ms  | $0.000418 |
| Ministral 3B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 1185ms  | $0.000254 |
| Ministral 8B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 1093ms  | $0.000621 |
| Claude 3 Haiku       | document_search   | `b35551a0f602` | 19,894    | ✓     | 3772ms  | $0.001951 |
| Llama 4 Scout 17B    | document_search   | `b35551a0f602` | 19,894    | ✓     | 1607ms  | $0.001053 |
| Nova Pro             | document_search   | `b35551a0f602` | 19,894    | ✓     | 1335ms  | $0.005160 |
| Llama 4 Maverick 17B | document_search   | `b35551a0f602` | 19,894    | ✓     | 1534ms  | $0.001061 |
| Ministral 14B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 2121ms  | $0.001265 |
| Claude Haiku 4.5     | document_search   | `b35551a0f602` | 19,894    | ✓     | 4640ms  | $0.007795 |
| Llama 3.3 70B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 1839ms  | $0.004510 |
| Devstral 2 123B      | document_search   | `b35551a0f602` | 19,894    | ✓     | 3204ms  | $0.003434 |
| DeepSeek V3.2        | document_search   | `b35551a0f602` | 19,894    | ✓     | 3470ms  | $0.003397 |
| Mistral Large 3      | document_search   | `b35551a0f602` | 19,894    | ✓     | 978ms   | $0.012776 |
| Claude Sonnet 4.5    | document_search   | `b35551a0f602` | 19,894    | ✓     | 7249ms  | $0.022261 |
| Magistral Small      | document_search   | `b35551a0f602` | 19,894    | ✓     | 3105ms  | $0.003370 |
| Devstral 2 123B      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 68965ms | $0.018934 |
| DeepSeek R1          | document_search   | `b35551a0f602` | 19,894    | ✓     | 4674ms  | $0.008964 |
| Claude Sonnet 4.6    | document_search   | `b35551a0f602` | 19,894    | ✓     | 9017ms  | $0.023157 |
| Nova Micro           | financial_manager | `aab5e628c929` | 45,820    | ✓     | 849ms   | $0.000450 |
| Nova Lite            | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1634ms  | $0.000800 |
| Ministral 3B         | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1603ms  | $0.000519 |
| Claude 3 Haiku       | financial_manager | `aab5e628c929` | 45,820    | ✓     | 4020ms  | $0.003447 |
| Llama 3.1 70B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 5100ms  | $0.004446 |
| Llama 4 Scout 17B    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2321ms  | $0.002176 |
| Ministral 8B         | financial_manager | `aab5e628c929` | 45,820    | ✗     | 3046ms  | $0.001298 |
| Claude Opus 4.1      | document_search   | `b35551a0f602` | 19,894    | ✓     | 14877ms | $0.103729 |
| Llama 4 Maverick 17B | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1526ms  | $0.002155 |
| Ministral 14B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2314ms  | $0.002566 |
| Nova Pro             | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2737ms  | $0.010793 |
| Llama 3.3 70B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2956ms  | $0.009185 |
| Claude Haiku 4.5     | financial_manager | `aab5e628c929` | 45,820    | ✗     | 7247ms  | $0.015461 |
| Devstral 2 123B      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 5832ms  | $0.007041 |
| DeepSeek V3.2        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 5528ms  | $0.006924 |
| Mistral Large 3      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2012ms  | $0.026986 |
| Claude Sonnet 4.5    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 12017ms | $0.045895 |
| Magistral Small      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 6811ms  | $0.007068 |
| Claude Sonnet 4.6    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 12671ms | $0.045539 |
| Nova Micro           | financial_manager | `04db50f097fc` | 74,649    | ✓     | 2394ms  | $0.000750 |
| DeepSeek R1          | financial_manager | `aab5e628c929` | 45,820    | ✓     | 12662ms | $0.018568 |
| Nova Lite            | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4167ms  | $0.001321 |
| Ministral 8B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3938ms  | $0.002043 |
| Ministral 3B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4193ms  | $0.000847 |
| Llama 4 Scout 17B    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3240ms  | $0.003432 |
| Claude 3 Haiku       | financial_manager | `04db50f097fc` | 74,649    | ✓     | 11141ms | $0.005934 |
| Claude Opus 4.1      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 24344ms | $0.211193 |
| Ministral 14B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3742ms  | $0.004059 |
| Llama 4 Maverick 17B | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3625ms  | $0.003476 |
| Nova Pro             | financial_manager | `04db50f097fc` | 74,649    | ✓     | 5469ms  | $0.017378 |
| Claude Haiku 4.5     | financial_manager | `04db50f097fc` | 74,649    | ✓     | 12103ms | $0.025413 |
| Llama 3.3 70B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4167ms  | $0.014588 |
| DeepSeek V3.2        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 9797ms  | $0.010880 |
| Claude Sonnet 4.5    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 22692ms | $0.073809 |
| Mistral Large 3      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 5696ms  | $0.042469 |
| Claude Sonnet 4.6    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 20024ms | $0.073003 |
| Llama 3.1 70B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 52712ms | $0.009168 |
| Magistral Small      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 7548ms  | $0.010722 |
| Nova Micro           | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 4493ms  | $0.001312 |
| Claude Opus 4.1      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 36423ms | $0.334076 |
| DeepSeek R1          | financial_manager | `04db50f097fc` | 74,649    | ✓     | 21774ms | $0.029190 |
| Ministral 3B         | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 4252ms  | $0.001465 |
| Claude 3 Haiku       | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 8247ms  | $0.009694 |
| Devstral 2 123B      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 67561ms | $0.010912 |
| Ministral 8B         | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 9889ms  | $0.003670 |
| Claude Haiku 4.5     | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5880ms  | $0.038801 |
| Ministral 14B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 9062ms  | $0.007339 |
| Nova Lite            | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 35196ms | $0.002559 |
| Llama 4 Maverick 17B | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5017ms  | $0.006248 |
| Claude Sonnet 4.5    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 12139ms | $0.118072 |
| Llama 4 Scout 17B    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 39628ms | $0.006538 |
| Devstral 2 123B      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 15920ms | $0.018907 |
| Llama 3.3 70B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 16977ms | $0.027011 |
| Claude Sonnet 4.6    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 10863ms | $0.116598 |
| DeepSeek V3.2        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 12592ms | $0.019245 |
| Mistral Large 3      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 17229ms | $0.075599 |
| Claude Opus 4.1      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 37869ms | $0.582652 |
| DeepSeek R1          | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 24758ms | $0.050938 |
| Magistral Small      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 71542ms | $0.019125 |
| Ministral 3B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✗     | 673ms   | $0.000065 |
| Nova Micro           | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 848ms   | $0.000060 |
| Ministral 8B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 946ms   | $0.000165 |
| Llama 4 Scout 17B    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 965ms   | $0.000273 |
| Nova Lite            | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1121ms  | $0.000119 |
| Ministral 14B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✗     | 644ms   | $0.000317 |
| Llama 4 Maverick 17B | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 794ms   | $0.000277 |
| Claude 3 Haiku       | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2120ms  | $0.000625 |
| Nova Pro             | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1504ms  | $0.001589 |
| Nova 2 Lite          | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 949ms   | $0.000111 |
| Claude Haiku 4.5     | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2435ms  | $0.002217 |
| Llama 3.3 70B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 993ms   | $0.001150 |
| Devstral 2 123B      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1995ms  | $0.001007 |
| DeepSeek V3.2        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1555ms  | $0.000934 |
| Mistral Large 3      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1319ms  | $0.003674 |
| Claude Sonnet 4.5    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3738ms  | $0.006558 |
| Nova Micro           | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 591ms   | $0.000061 |
| Magistral Small      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1827ms  | $0.000969 |
| Nova Lite            | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 874ms   | $0.000118 |
| Ministral 3B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 414ms   | $0.000065 |
| Claude 3 Haiku       | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1543ms  | $0.000557 |
| Claude Sonnet 4.6    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3956ms  | $0.006734 |
| Llama 4 Scout 17B    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 977ms   | $0.000284 |
| Ministral 8B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1346ms  | $0.000183 |
| DeepSeek R1          | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3425ms  | $0.002610 |
| Nova Pro             | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1033ms  | $0.001617 |
| Llama 4 Maverick 17B | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1109ms  | $0.000291 |
| Ministral 14B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1279ms  | $0.000347 |
| Nova 2 Lite          | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 894ms   | $0.000116 |
| Claude Haiku 4.5     | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2654ms  | $0.002587 |
| Claude Opus 4.1      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 6328ms  | $0.030746 |
| Llama 3.3 70B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1162ms  | $0.001223 |
| DeepSeek V3.2        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1533ms  | $0.001043 |
| Devstral 2 123B      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2934ms  | $0.001059 |
| Claude Sonnet 4.5    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 4151ms  | $0.006991 |
| Nova Micro           | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 609ms   | $0.000062 |
| Magistral Small      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2141ms  | $0.001035 |
| Nova Lite            | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1014ms  | $0.000116 |
| Ministral 3B         | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 509ms   | $0.000066 |
| Claude 3 Haiku       | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1615ms  | $0.000560 |
| Claude Sonnet 4.6    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 5204ms  | $0.007895 |
| Ministral 8B         | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 908ms   | $0.000169 |
| Llama 4 Scout 17B    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 684ms   | $0.000279 |
| Mistral Large 3      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 5370ms  | $0.003952 |
| Nova Pro             | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1009ms  | $0.001544 |
| Llama 4 Maverick 17B | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 724ms   | $0.000279 |
| Ministral 14B        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 975ms   | $0.000340 |
| DeepSeek R1          | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 5203ms  | $0.002879 |
| Nova 2 Lite          | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 959ms   | $0.000113 |
| Llama 3.3 70B        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1211ms  | $0.001216 |
| Claude Haiku 4.5     | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 3214ms  | $0.002677 |
| Devstral 2 123B      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 2347ms  | $0.001094 |
| DeepSeek V3.2        | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1942ms  | $0.001000 |
| Mistral Large 3      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 967ms   | $0.003903 |
| Magistral Small      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 1617ms  | $0.000978 |
| Claude Sonnet 4.5    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 5127ms  | $0.006718 |
| Nova Micro           | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1092ms  | $0.000084 |
| Nova Lite            | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1081ms  | $0.000166 |
| Claude Opus 4.1      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 12418ms | $0.035291 |
| DeepSeek R1          | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 3360ms  | $0.002873 |
| Ministral 3B         | document_search   | `564670dcb6b9` | 4,720     | ✓     | 885ms   | $0.000100 |
| Ministral 8B         | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1123ms  | $0.000244 |
| Claude Sonnet 4.6    | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 5710ms  | $0.007025 |
| Llama 4 Scout 17B    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1108ms  | $0.000403 |
| Nova Pro             | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1024ms  | $0.002169 |
| Claude 3 Haiku       | document_search   | `564670dcb6b9` | 4,720     | ✓     | 3358ms  | $0.000852 |
| Llama 4 Maverick 17B | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1113ms  | $0.000406 |
| Ministral 14B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1739ms  | $0.000495 |
| Claude Opus 4.1      | git_operations    | `b0b7c4f19e15` | 2,154     | ✓     | 8128ms  | $0.030270 |
| Nova 2 Lite          | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1077ms  | $0.000169 |
| Claude Haiku 4.5     | document_search   | `564670dcb6b9` | 4,720     | ✓     | 4369ms  | $0.003665 |
| Llama 3.3 70B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2205ms  | $0.001715 |
| Devstral 2 123B      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2944ms  | $0.001528 |
| Mistral Large 3      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 819ms   | $0.005296 |
| DeepSeek V3.2        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2472ms  | $0.001445 |
| Magistral Small      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1725ms  | $0.001335 |
| Claude Sonnet 4.5    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 6628ms  | $0.010028 |
| Nova Micro           | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 2726ms  | $0.001277 |
| DeepSeek R1          | document_search   | `564670dcb6b9` | 4,720     | ✓     | 3753ms  | $0.003896 |
| Claude Sonnet 4.6    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 6890ms  | $0.010973 |
| Ministral 3B         | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3225ms  | $0.001450 |
| Ministral 8B         | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3705ms  | $0.003599 |
| Nova Lite            | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 6260ms  | $0.002270 |
| Llama 4 Scout 17B    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3847ms  | $0.006118 |
| Claude Opus 4.1      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 12597ms | $0.043841 |
| Llama 4 Maverick 17B | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 4240ms  | $0.006148 |
| Ministral 14B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 4924ms  | $0.007203 |
| Nova 2 Lite          | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3907ms  | $0.002177 |
| Claude 3 Haiku       | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 19669ms | $0.011388 |
| Claude Haiku 4.5     | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 16320ms | $0.041896 |
| Llama 3.3 70B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 7249ms  | $0.026221 |
| Nova Pro             | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 40369ms | $0.035061 |
| Mistral Large 3      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 9610ms  | $0.075551 |
| Claude Sonnet 4.6    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 35676ms | $0.126707 |
| Claude Sonnet 4.5    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 52462ms | $0.135141 |
| Magistral Small      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 6787ms  | $0.018236 |
| Nova Micro           | document_search   | `b35551a0f602` | 19,894    | ✓     | 872ms   | $0.000220 |
| Nova Lite            | document_search   | `b35551a0f602` | 19,894    | ✓     | 2528ms  | $0.000417 |
| Ministral 3B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 1048ms  | $0.000248 |
| DeepSeek V3.2        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 45884ms | $0.025235 |
| Claude 3 Haiku       | document_search   | `b35551a0f602` | 19,894    | ✓     | 3749ms  | $0.001922 |
| Llama 4 Scout 17B    | document_search   | `b35551a0f602` | 19,894    | ✓     | 1445ms  | $0.001056 |
| Claude Opus 4.1      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 46621ms | $0.572392 |
| Nova Pro             | document_search   | `b35551a0f602` | 19,894    | ✓     | 2627ms  | $0.005206 |
| Ministral 8B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 4442ms  | $0.000634 |
| Ministral 14B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 2051ms  | $0.001264 |
| Llama 4 Maverick 17B | document_search   | `b35551a0f602` | 19,894    | ✓     | 1161ms  | $0.001045 |
| Claude Haiku 4.5     | document_search   | `b35551a0f602` | 19,894    | ✓     | 4671ms  | $0.007713 |
| Nova 2 Lite          | document_search   | `b35551a0f602` | 19,894    | ✓     | 1387ms  | $0.000393 |
| Llama 3.3 70B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 1646ms  | $0.004469 |
| DeepSeek R1          | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 18270ms | $0.050034 |
| Devstral 2 123B      | document_search   | `b35551a0f602` | 19,894    | ✓     | 3452ms  | $0.003425 |
| Mistral Large 3      | document_search   | `b35551a0f602` | 19,894    | ✓     | 1006ms  | $0.012927 |
| Magistral Small      | document_search   | `b35551a0f602` | 19,894    | ✓     | 3466ms  | $0.003419 |
| Claude Sonnet 4.5    | document_search   | `b35551a0f602` | 19,894    | ✓     | 9123ms  | $0.022984 |
| Nova Micro           | financial_manager | `aab5e628c929` | 45,820    | ✓     | 849ms   | $0.000449 |
| Claude Sonnet 4.6    | document_search   | `b35551a0f602` | 19,894    | ✓     | 8826ms  | $0.022932 |
| Nova Lite            | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1516ms  | $0.000793 |
| DeepSeek R1          | document_search   | `b35551a0f602` | 19,894    | ✓     | 4321ms  | $0.009004 |
| DeepSeek V3.2        | document_search   | `b35551a0f602` | 19,894    | ✓     | 12085ms | $0.003402 |
| Claude 3 Haiku       | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3184ms  | $0.003454 |
| Ministral 3B         | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3589ms  | $0.000522 |
| Devstral 2 123B      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 74766ms | $0.019685 |
| Llama 4 Scout 17B    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2846ms  | $0.002175 |
| Ministral 8B         | financial_manager | `aab5e628c929` | 45,820    | ✗     | 4124ms  | $0.001283 |
| Nova Pro             | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2267ms  | $0.010738 |
| Llama 4 Maverick 17B | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1804ms  | $0.002164 |
| Ministral 14B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3362ms  | $0.002600 |
| Claude Opus 4.1      | document_search   | `b35551a0f602` | 19,894    | ✓     | 15835ms | $0.104179 |
| Nova 2 Lite          | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2391ms  | $0.000815 |
| Llama 3.3 70B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2806ms  | $0.009213 |
| Claude Haiku 4.5     | financial_manager | `aab5e628c929` | 45,820    | ✗     | 7541ms  | $0.015718 |
| DeepSeek V3.2        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 4686ms  | $0.007051 |
| Devstral 2 123B      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 5868ms  | $0.006853 |
| Mistral Large 3      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2823ms  | $0.027588 |
| Nova Micro           | financial_manager | `04db50f097fc` | 74,649    | ✓     | 2416ms  | $0.000745 |
| Magistral Small      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 4565ms  | $0.006808 |
| Nova Lite            | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3656ms  | $0.001306 |
| Claude Sonnet 4.5    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 14410ms | $0.046874 |
| Claude Sonnet 4.6    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 13059ms | $0.045486 |
| Llama 4 Scout 17B    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 2934ms  | $0.003432 |
| Ministral 3B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 5276ms  | $0.000841 |
| Ministral 8B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 7131ms  | $0.002053 |
| DeepSeek R1          | financial_manager | `aab5e628c929` | 45,820    | ✓     | 14739ms | $0.018768 |
| Claude 3 Haiku       | financial_manager | `04db50f097fc` | 74,649    | ✓     | 10316ms | $0.005994 |
| Nova Pro             | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4358ms  | $0.017331 |
| Ministral 14B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4073ms  | $0.004067 |
| Llama 4 Maverick 17B | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4359ms  | $0.003485 |
| Claude Opus 4.1      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 23014ms | $0.210536 |
| Nova 2 Lite          | financial_manager | `04db50f097fc` | 74,649    | ✗     | 3419ms  | $0.001282 |
| Claude Haiku 4.5     | financial_manager | `04db50f097fc` | 74,649    | ✓     | 10508ms | $0.024657 |
| Llama 3.3 70B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3542ms  | $0.014582 |
| Devstral 2 123B      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 8869ms  | $0.010963 |
| DeepSeek V3.2        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 9274ms  | $0.011490 |
| Magistral Small      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 7227ms  | $0.010661 |
| Claude Sonnet 4.5    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 23425ms | $0.074244 |
| Claude Sonnet 4.6    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 20777ms | $0.073382 |
| Mistral Large 3      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 21193ms | $0.042728 |
| DeepSeek R1          | financial_manager | `04db50f097fc` | 74,649    | ✓     | 18012ms | $0.029306 |
| Claude 3 Haiku       | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 7231ms  | $0.009603 |
| Ministral 8B         | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 6812ms  | $0.003672 |
| Nova Micro           | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 21559ms | $0.001472 |
| Claude Opus 4.1      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 34969ms | $0.333157 |
| Claude Haiku 4.5     | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5483ms  | $0.038597 |
| Llama 4 Maverick 17B | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 4767ms  | $0.006239 |
| Ministral 3B         | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 24236ms | $0.001528 |
| Nova 2 Lite          | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 3679ms  | $0.002193 |
| Nova Lite            | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 35399ms | $0.002549 |
| Claude Sonnet 4.5    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 14179ms | $0.118953 |
| Llama 4 Scout 17B    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 38063ms | $0.006550 |
| DeepSeek V3.2        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 11398ms | $0.019118 |
| Llama 3.3 70B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 24004ms | $0.027667 |
| Claude Sonnet 4.6    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 12140ms | $0.117138 |
| Ministral 14B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 46567ms | $0.007596 |
| Mistral Large 3      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 18079ms | $0.075515 |
| Magistral Small      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 17445ms | $0.019354 |
| Claude Opus 4.1      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 35670ms | $0.583196 |
| DeepSeek R1          | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 33020ms | $0.050066 |
| Nova Micro           | git_operations    | `3224d192da4f` | 120,021   | ✓     | 3586ms  | $0.001137 |
| Llama 4 Scout 17B    | git_operations    | `3224d192da4f` | 120,021   | ✓     | 4354ms  | $0.005369 |
| Nova Lite            | git_operations    | `3224d192da4f` | 120,021   | ✓     | 6292ms  | $0.001990 |
| Claude 3 Haiku       | git_operations    | `3224d192da4f` | 120,021   | ✓     | 6821ms  | $0.008292 |
| Ministral 3B         | git_operations    | `3224d192da4f` | 120,021   | ✓     | 9445ms  | $0.001262 |
| Llama 4 Maverick 17B | git_operations    | `3224d192da4f` | 120,021   | ✓     | 4859ms  | $0.005402 |
| Ministral 14B        | git_operations    | `3224d192da4f` | 120,021   | ✓     | 5635ms  | $0.006337 |
| Claude Haiku 4.5     | git_operations    | `3224d192da4f` | 120,021   | ✓     | 9688ms  | $0.035299 |
| Nova Pro             | git_operations    | `3224d192da4f` | 120,021   | ✓     | 9585ms  | $0.026183 |
| Nova 2 Lite          | git_operations    | `3224d192da4f` | 120,021   | ✓     | 2488ms  | $0.001899 |
| Llama 3.3 70B        | git_operations    | `3224d192da4f` | 120,021   | ✓     | 6032ms  | $0.022835 |
| Ministral 8B         | git_operations    | `3224d192da4f` | 120,021   | ✓     | 20200ms | $0.003166 |
| DeepSeek V3.2        | git_operations    | `3224d192da4f` | 120,021   | ✓     | 10924ms | $0.016509 |
| Claude Sonnet 4.6    | git_operations    | `3224d192da4f` | 120,021   | ✓     | 17946ms | $0.103354 |
| Mistral Large 3      | git_operations    | `3224d192da4f` | 120,021   | ✓     | 12972ms | $0.064880 |
| Claude Sonnet 4.5    | git_operations    | `3224d192da4f` | 120,021   | ✓     | 24404ms | $0.108225 |
| Nova Micro           | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 656ms   | $0.000061 |
| Nova Lite            | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1143ms  | $0.000119 |
| Claude 3 Haiku       | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2199ms  | $0.000607 |
| Ministral 8B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 759ms   | $0.000165 |
| Magistral Small      | git_operations    | `3224d192da4f` | 120,021   | ✓     | 11896ms | $0.016478 |
| Llama 4 Scout 17B    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1172ms  | $0.000272 |
| Nova Pro             | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1157ms  | $0.001528 |
| Claude Haiku 4.5     | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2354ms  | $0.002396 |
| Ministral 3B         | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 4773ms  | $0.000065 |
| Llama 4 Maverick 17B | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 966ms   | $0.000277 |
| Ministral 14B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 972ms   | $0.000324 |
| Nova 2 Lite          | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1063ms  | $0.000111 |
| Llama 3.3 70B        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1033ms  | $0.001150 |
| Claude Sonnet 4.5    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3886ms  | $0.006386 |
| DeepSeek V3.2        | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 2535ms  | $0.000972 |
| DeepSeek R1          | git_operations    | `3224d192da4f` | 120,021   | ✓     | 15142ms | $0.044125 |
| Claude Sonnet 4.6    | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 4543ms  | $0.006884 |
| Magistral Small      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 1937ms  | $0.000967 |
| Mistral Large 3      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 3554ms  | $0.003798 |
| Nova Micro           | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 635ms   | $0.000060 |
| Nova Lite            | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 869ms   | $0.000117 |
| Claude 3 Haiku       | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2365ms  | $0.000584 |
| Claude Opus 4.1      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 10510ms | $0.032002 |
| Ministral 3B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 608ms   | $0.000068 |
| Llama 4 Scout 17B    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 987ms   | $0.000287 |
| Devstral 2 123B      | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 17130ms | $0.001037 |
| Nova Pro             | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1163ms  | $0.001641 |
| DeepSeek R1          | git_operations    | `b18a91ab5fd4` | 1,971     | ✓     | 8347ms  | $0.002614 |
| Claude Haiku 4.5     | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2472ms  | $0.002493 |
| Ministral 14B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1081ms  | $0.000342 |
| Llama 4 Maverick 17B | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1070ms  | $0.000291 |
| Nova 2 Lite          | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1172ms  | $0.000116 |
| Claude Opus 4.1      | git_operations    | `3224d192da4f` | 120,021   | ✓     | 41435ms | $0.505012 |
| Devstral 2 123B      | git_operations    | `3224d192da4f` | 120,021   | ✓     | 50025ms | $0.016466 |
| Llama 3.3 70B        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1233ms  | $0.001220 |
| Claude Sonnet 4.5    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 4447ms  | $0.006991 |
| Mistral Large 3      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 1066ms  | $0.003980 |
| Claude Sonnet 4.6    | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 4700ms  | $0.007388 |
| Magistral Small      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 2159ms  | $0.001040 |
| DeepSeek V3.2        | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 6282ms  | $0.001055 |
| Nova Micro           | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1255ms  | $0.000084 |
| Ministral 8B         | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 12826ms | $0.000181 |
| Nova Lite            | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1129ms  | $0.000171 |
| DeepSeek R1          | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 3011ms  | $0.002908 |
| Llama 4 Scout 17B    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 982ms   | $0.000403 |
| Claude 3 Haiku       | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2865ms  | $0.000898 |
| Nova Pro             | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1234ms  | $0.002143 |
| Ministral 14B        | document_search   | `564670dcb6b9` | 4,720     | ✗     | 1816ms  | $0.000502 |
| Claude Haiku 4.5     | document_search   | `564670dcb6b9` | 4,720     | ✓     | 3339ms  | $0.003590 |
| Claude Opus 4.1      | git_operations    | `039bf3ebe0f0` | 2,160     | ✓     | 12995ms | $0.035141 |
| Llama 4 Maverick 17B | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1206ms  | $0.000407 |
| Nova 2 Lite          | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1224ms  | $0.000168 |
| Llama 3.3 70B        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 1285ms  | $0.001696 |
| Claude Sonnet 4.5    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 6495ms  | $0.010216 |
| DeepSeek V3.2        | document_search   | `564670dcb6b9` | 4,720     | ✓     | 2917ms  | $0.001413 |
| Claude Sonnet 4.6    | document_search   | `564670dcb6b9` | 4,720     | ✓     | 6157ms  | $0.010793 |
| Mistral Large 3      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 962ms   | $0.005281 |
| Magistral Small      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 3000ms  | $0.001564 |
| Claude Opus 4.1      | document_search   | `564670dcb6b9` | 4,720     | ✓     | 10809ms | $0.043804 |
| Nova Micro           | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 2950ms  | $0.001279 |
| DeepSeek R1          | document_search   | `564670dcb6b9` | 4,720     | ✓     | 4549ms  | $0.003795 |
| Nova Lite            | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 6119ms  | $0.002248 |
| Ministral 8B         | document_search   | `564670dcb6b9` | 4,720     | ✓     | 36070ms | $0.000243 |
| Ministral 3B         | document_search   | `564670dcb6b9` | 4,720     | ✓     | 37187ms | $0.000101 |
| Llama 4 Scout 17B    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 4286ms  | $0.006117 |
| Ministral 8B         | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 10434ms | $0.003630 |
| Claude 3 Haiku       | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 19476ms | $0.011396 |
| Ministral 14B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 5163ms  | $0.007208 |
| Llama 4 Maverick 17B | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 3742ms  | $0.006123 |
| Claude Haiku 4.5     | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 18069ms | $0.042577 |
| Nova 2 Lite          | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 15782ms | $0.002713 |
| Ministral 3B         | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 44515ms | $0.001530 |
| Llama 3.3 70B        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 6927ms  | $0.026055 |
| Nova Pro             | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 41535ms | $0.035487 |
| Claude Sonnet 4.5    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 41476ms | $0.129137 |
| DeepSeek V3.2        | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 30598ms | $0.018979 |
| Claude Sonnet 4.6    | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 30942ms | $0.124108 |
| Magistral Small      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 5913ms  | $0.018087 |
| Nova Micro           | document_search   | `b35551a0f602` | 19,894    | ✓     | 733ms   | $0.000220 |
| Nova Lite            | document_search   | `b35551a0f602` | 19,894    | ✓     | 2241ms  | $0.000416 |
| Claude 3 Haiku       | document_search   | `b35551a0f602` | 19,894    | ✓     | 4190ms  | $0.001853 |
| Mistral Large 3      | document_search   | `57ed3fb8960d` | 120,021   | ✗     | 17901ms | $0.074558 |
| Ministral 8B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 2683ms  | $0.000633 |
| Llama 4 Scout 17B    | document_search   | `b35551a0f602` | 19,894    | ✓     | 1612ms  | $0.001055 |
| Nova Pro             | document_search   | `b35551a0f602` | 19,894    | ✓     | 1700ms  | $0.005143 |
| DeepSeek R1          | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 15906ms | $0.050031 |
| Claude Haiku 4.5     | document_search   | `b35551a0f602` | 19,894    | ✓     | 4551ms  | $0.007700 |
| Ministral 14B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 1810ms  | $0.001257 |
| Llama 4 Maverick 17B | document_search   | `b35551a0f602` | 19,894    | ✓     | 1135ms  | $0.001050 |
| Nova 2 Lite          | document_search   | `b35551a0f602` | 19,894    | ✓     | 1615ms  | $0.000392 |
| Llama 3.3 70B        | document_search   | `b35551a0f602` | 19,894    | ✓     | 1708ms  | $0.004455 |
| Claude Opus 4.1      | document_search   | `57ed3fb8960d` | 120,021   | ✓     | 45319ms | $0.574324 |
| DeepSeek V3.2        | document_search   | `b35551a0f602` | 19,894    | ✓     | 4621ms  | $0.003432 |
| Claude Sonnet 4.5    | document_search   | `b35551a0f602` | 19,894    | ✓     | 8678ms  | $0.023044 |
| Ministral 3B         | document_search   | `b35551a0f602` | 19,894    | ✓     | 16485ms | $0.000252 |
| Mistral Large 3      | document_search   | `b35551a0f602` | 19,894    | ✓     | 1247ms  | $0.013035 |
| Magistral Small      | document_search   | `b35551a0f602` | 19,894    | ✓     | 2891ms  | $0.003333 |
| Nova Micro           | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1176ms  | $0.000458 |
| DeepSeek R1          | document_search   | `b35551a0f602` | 19,894    | ✓     | 4772ms  | $0.009116 |
| Nova Lite            | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2137ms  | $0.000824 |
| Claude Sonnet 4.6    | document_search   | `b35551a0f602` | 19,894    | ✓     | 8956ms  | $0.023194 |
| Claude 3 Haiku       | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3866ms  | $0.003464 |
| Ministral 3B         | financial_manager | `aab5e628c929` | 45,820    | ✓     | 4308ms  | $0.000528 |
| Claude Opus 4.1      | document_search   | `b35551a0f602` | 19,894    | ✓     | 11281ms | $0.101441 |
| Ministral 8B         | financial_manager | `aab5e628c929` | 45,820    | ✗     | 4200ms  | $0.001306 |
| Llama 4 Scout 17B    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2251ms  | $0.002164 |
| Llama 4 Maverick 17B | financial_manager | `aab5e628c929` | 45,820    | ✓     | 1625ms  | $0.002165 |
| Nova Pro             | financial_manager | `aab5e628c929` | 45,820    | ✓     | 2677ms  | $0.010750 |
| Ministral 14B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 4336ms  | $0.002636 |
| Nova 2 Lite          | financial_manager | `aab5e628c929` | 45,820    | ✗     | 2984ms  | $0.000805 |
| Claude Haiku 4.5     | financial_manager | `aab5e628c929` | 45,820    | ✗     | 8137ms  | $0.016001 |
| Llama 3.3 70B        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3662ms  | $0.009268 |
| Claude Sonnet 4.5    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 13428ms | $0.045437 |
| DeepSeek V3.2        | financial_manager | `aab5e628c929` | 45,820    | ✓     | 13005ms | $0.006963 |
| Claude Sonnet 4.6    | financial_manager | `aab5e628c929` | 45,820    | ✓     | 14689ms | $0.045944 |
| Mistral Large 3      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 3537ms  | $0.028234 |
| Magistral Small      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 6529ms  | $0.007010 |
| Nova Micro           | financial_manager | `04db50f097fc` | 74,649    | ✓     | 2320ms  | $0.000749 |
| DeepSeek R1          | financial_manager | `aab5e628c929` | 45,820    | ✓     | 8866ms  | $0.018027 |
| Nova Lite            | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4973ms  | $0.001339 |
| Claude Opus 4.1      | financial_manager | `aab5e628c929` | 45,820    | ✓     | 23416ms | $0.211080 |
| Claude 3 Haiku       | financial_manager | `04db50f097fc` | 74,649    | ✓     | 6364ms  | $0.005446 |
| Llama 4 Scout 17B    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 2893ms  | $0.003432 |
| Nova Pro             | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4985ms  | $0.017578 |
| Claude Haiku 4.5     | financial_manager | `04db50f097fc` | 74,649    | ✓     | 10539ms | $0.024734 |
| Ministral 14B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3686ms  | $0.004070 |
| Ministral 8B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 12112ms | $0.002030 |
| Llama 4 Maverick 17B | financial_manager | `04db50f097fc` | 74,649    | ✓     | 3432ms  | $0.003458 |
| Nova 2 Lite          | financial_manager | `04db50f097fc` | 74,649    | ✗     | 3251ms  | $0.001285 |
| Llama 3.3 70B        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 4947ms  | $0.014648 |
| DeepSeek V3.2        | financial_manager | `04db50f097fc` | 74,649    | ✓     | 13011ms | $0.011060 |
| Ministral 3B         | financial_manager | `04db50f097fc` | 74,649    | ✓     | 37408ms | $0.000834 |
| Claude Sonnet 4.5    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 26848ms | $0.076801 |
| Mistral Large 3      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 17241ms | $0.047692 |
| Claude Sonnet 4.6    | financial_manager | `04db50f097fc` | 74,649    | ✓     | 23120ms | $0.074810 |
| Magistral Small      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 7382ms  | $0.010697 |
| Claude Opus 4.1      | financial_manager | `04db50f097fc` | 74,649    | ✓     | 30593ms | $0.331282 |
| Nova Micro           | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 3959ms  | $0.001294 |
| DeepSeek R1          | financial_manager | `04db50f097fc` | 74,649    | ✓     | 14350ms | $0.029010 |
| Claude 3 Haiku       | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 7142ms  | $0.009632 |
| Claude Haiku 4.5     | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5853ms  | $0.038836 |
| Nova Lite            | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 35719ms | $0.002593 |
| Ministral 3B         | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 37762ms | $0.001500 |
| Ministral 14B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 8318ms  | $0.007330 |
| Llama 4 Maverick 17B | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5269ms  | $0.006246 |
| Nova 2 Lite          | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 2870ms  | $0.002195 |
| Llama 4 Scout 17B    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 39796ms | $0.006552 |
| Llama 3.3 70B        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 5382ms  | $0.026202 |
| Claude Sonnet 4.5    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 11543ms | $0.117506 |
| Claude Sonnet 4.6    | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 10863ms | $0.116579 |
| DeepSeek V3.2        | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 14282ms | $0.019249 |
| Mistral Large 3      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 11639ms | $0.075593 |
| Claude Opus 4.1      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 17688ms | $0.582521 |
| DeepSeek R1          | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 16641ms | $0.050829 |
| Magistral Small      | financial_manager | `c9700ee2c39b` | 120,021   | ✓     | 77333ms | $0.019239 |
