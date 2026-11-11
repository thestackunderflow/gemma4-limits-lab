### P-DEF: default context, fresh load, no options
| model | digest | /api/ps context_length | PROCESSOR | layers on GPU | server log line |
|---|---|---|---|---|---|
| e2b | b37049369adf | 4096 | 100% GPU | [36, 36] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |
| e4b | dc35e8d9c606 | 4096 | 100% GPU | [43, 43] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |
| 12b-qat | 38044be4f923 | 4096 | 3%/97% CPU/GPU | [38, 49] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |

### P-TRUNC: a ~9.6K-token prompt (fact = line 1 or last line)
| model | endpoint | fact at | extra | num_ctx | sampling | HTTP | prompt_eval_count | right | of | WARN in log | error |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e4b | chat | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | chat | end | {} | default (no option) | temp 0 | [200] | [2051] | 3 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | generate | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | generate | end | {} | default (no option) | temp 0 | [200] | [2051] | 3 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | openai | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | openai | end | {} | default (no option) | temp 0 | [200] | [2051] | 3 | 3 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | chat | start | {"truncate": false} | default (no option) | temp 0 | [400] | [] | 0 | 3 |  | request (9644 tokens) exceeds the available context size (4096 tokens), try increasing it |
| e4b | generate | start | {"truncate": false} | default (no option) | temp 0 | [400] | [] | 0 | 3 |  | request (9644 tokens) exceeds the available context size (4096 tokens), try increasing it |
| e4b | chat | start | {"shift": false} | default (no option) | temp 0 | [400] | [] | 0 | 3 |  | the prompt is longer than the context length currently available to the model; shorten the prompt, adjust the context length in settings, or use a model with a longer context length |
| e4b | generate | start | {"shift": false} | default (no option) | temp 0 | [400] | [] | 0 | 3 |  | the prompt is longer than the context length currently available to the model; shorten the prompt, adjust the context length in settings, or use a model with a longer context length |
| e4b | chat | start | {} | 16384 | temp 0 | [200] | [9644] | 3 | 3 |  |  |
| e4b | chat | end | {} | 16384 | temp 0 | [200] | [9644] | 3 | 3 |  |  |
| 12b-qat | chat | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 1 | {'limit': 2051, 'prompt': 9648, 'keep': 5, 'new': 2051} |  |
| 12b-qat | chat | end | {} | default (no option) | temp 0 | [200] | [2051] | 1 | 1 | {'limit': 2051, 'prompt': 9648, 'keep': 5, 'new': 2051} |  |
| 12b-qat | openai | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 1 | {'limit': 2051, 'prompt': 9648, 'keep': 5, 'new': 2051} |  |
| 12b-qat | openai | end | {} | default (no option) | temp 0 | [200] | [2051] | 1 | 1 | {'limit': 2051, 'prompt': 9648, 'keep': 5, 'new': 2051} |  |
| 12b-qat | chat | start | {} | 16384 | temp 0 | [200] | [9648] | 1 | 1 |  |  |
| 12b-qat | chat | end | {} | 16384 | temp 0 | [200] | [9648] | 1 | 1 |  |  |
| e4b | chat | start | {} | default (no option) | google-recommended temp 1.0 | [200] | [2051] | 0 | 5 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | chat | start | {} | 16384 | google-recommended temp 1.0 | [200] | [9644] | 5 | 5 |  |  |

### P-FIT: what loads (3 fresh loads per cell, medians)
| model | KV set | num_ctx | kind | loads | KV in log | PROCESSOR | layers GPU | GPU MiB max | container MiB max | prompt tok | prefill tok/s | write tok/s | prefill s | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 12b-qat | f16 | 65536 | speed | 3/3 | ['f16'] | ['5%/95% CPU/GPU'] | [(31, 49)] | 7208.0 | 2222.1 | 16216 | 788.0 | 12.8 | 20.6 |  |
| 12b-qat | f16 | 131072 | speed | 3/3 | ['f16'] | ['8%/92% CPU/GPU'] | [(26, 49)] | 7388.0 | 2733.1 | 16216 | 705.4 | 11.0 | 22.9 |  |
| 12b-qat | f16 | 262144 | max-fill | 1/1 | ['f16'] | ['13%/87% CPU/GPU'] | [(19, 49)] | 7116.0 | 4845.6 | 251709 | 300.9 | 1.4 | 836.4 |  |
| 12b-qat | f16 | 262144 | speed | 3/3 | ['f16'] | ['13%/87% CPU/GPU'] | [(19, 49)] | 7116.0 | 4727.8 | 16216 | 611.1 | 8.4 | 26.5 |  |
| 12b-qat | q8_0 | 65536 | speed | 3/3 | ['q8_0'] | ['3%/97% CPU/GPU'] | [(35, 49)] | 7277.0 | 1591.3 | 16216 | 879.0 | 13.6 | 18.4 |  |
| 12b-qat | q8_0 | 131072 | speed | 3/3 | ['q8_0'] | ['5%/95% CPU/GPU'] | [(30, 49)] | 7181.0 | 1958.9 | 16216 | 775.5 | 11.4 | 20.9 |  |
| 12b-qat | q8_0 | 262144 | max-fill | 1/1 | ['q8_0'] | ['8%/92% CPU/GPU'] | [(23, 49)] | 7231.0 | 2927.6 | 251709 | 322.9 | 4.2 | 779.5 |  |
| 12b-qat | q8_0 | 262144 | speed | 3/3 | ['q8_0'] | ['8%/92% CPU/GPU'] | [(23, 49)] | 7229.0 | 2816.0 | 16216 | 667.7 | 9.5 | 24.3 |  |
| e2b | f16 | 4096 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(36, 36)] | 4198.0 | 1157.1 | 2168 | 5371.9 | 115.9 | 0.4 |  |
| e2b | f16 | 16384 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(36, 36)] | 4436.0 | 1216.5 | 8086 | 10051.4 | 125.5 | 0.8 |  |
| e2b | f16 | 32768 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(36, 36)] | 4596.0 | 1381.4 | 16212 | 11377.0 | 109.1 | 1.4 |  |
| e2b | f16 | 65536 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(36, 36)] | 4678.0 | 1289.2 | 16212 | 11571.5 | 108.3 | 1.4 |  |
| e2b | f16 | 131072 | max-fill | 1/1 | ['f16'] | ['100% GPU'] | [(36, 36)] | 5180.0 | 1522.7 | 125125 | 4748.0 | 61.6 | 26.4 |  |
| e2b | f16 | 131072 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(36, 36)] | 5190.0 | 1469.4 | 16212 | 11441.3 | 105.6 | 1.4 |  |
| e2b | q8_0 | 4096 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 4078.0 |  | 2168 | 3955.3 | 116.4 | 0.5 |  |
| e2b | q8_0 | 16384 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 4318.0 |  | 8086 | 9719.4 | 124.9 | 0.8 |  |
| e2b | q8_0 | 32768 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 4496.0 |  | 16212 | 10881.2 | 99.2 | 1.5 |  |
| e2b | q8_0 | 65536 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 4632.0 |  | 16212 | 11080.7 | 102.3 | 1.5 |  |
| e2b | q8_0 | 131072 | max-fill | 1/1 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 5220.0 |  | 125125 | 4597.0 | 38.5 | 27.2 |  |
| e2b | q8_0 | 131072 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(36, 36)] | 5220.0 |  | 16212 | 10780.1 | 99.9 | 1.5 |  |
| e4b | f16 | 4096 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(43, 43)] | 5842.0 | 4797.4 | 2168 | 2360.3 | 87.0 | 0.9 |  |
| e4b | f16 | 16384 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(43, 43)] | 6058.0 | 1281.0 | 8086 | 4250.6 | 78.2 | 1.9 |  |
| e4b | f16 | 32768 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(43, 43)] | 6346.0 | 1317.9 | 16212 | 4774.1 | 73.9 | 3.4 |  |
| e4b | f16 | 65536 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(43, 43)] | 6928.0 | 1382.4 | 16212 | 4776.5 | 74.2 | 3.4 |  |
| e4b | f16 | 131072 | max-fill | 1/1 | ['f16'] | ['100% GPU'] | [(40, 43)] | 7714.0 | 1506.3 | 125125 | 2391.7 | 35.5 | 52.3 |  |
| e4b | f16 | 131072 | speed | 3/3 | ['f16'] | ['100% GPU'] | [(40, 43)] | 7714.0 | 1502.2 | 16212 | 3767.3 | 61.1 | 4.3 |  |
| e4b | q8_0 | 4096 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 5728.0 | 4826.1 | 2168 | 2655.7 | 87.0 | 0.8 |  |
| e4b | q8_0 | 16384 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 5934.0 | 1189.9 | 8086 | 4178.8 | 72.0 | 1.9 |  |
| e4b | q8_0 | 32768 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 6230.0 | 1305.6 | 16212 | 4488.6 | 62.7 | 3.6 |  |
| e4b | q8_0 | 65536 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 6822.0 | 1371.1 | 16212 | 4636.4 | 65.9 | 3.5 |  |
| e4b | q8_0 | 131072 | max-fill | 1/1 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 7753.0 | 1557.5 | 125125 | 1578.4 | 23.4 | 79.3 |  |
| e4b | q8_0 | 131072 | speed | 3/3 | ['q8_0'] | ['100% GPU'] | [(43, 43)] | 7769.0 | 1434.6 | 16212 | 2166.1 | 63.0 | 7.5 |  |
