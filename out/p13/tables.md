### P-DEF: default context, fresh load, no options
| model | digest | /api/ps context_length | PROCESSOR | layers on GPU | server log line |
|---|---|---|---|---|---|
| e2b | b37049369adf | 4096 | 100% GPU | [36, 36] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |
| e4b | dc35e8d9c606 | 4096 | 100% GPU | [43, 43] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |
| 12b-qat | 38044be4f923 | 4096 | 3%/97% CPU/GPU | [38, 49] | {'total_vram': '8.0 GiB', 'default_num_ctx': 4096} |

### P-TRUNC: a ~9.6K-token prompt (fact = line 1 or last line)
| model | endpoint | fact at | extra | num_ctx | sampling | HTTP | prompt_eval_count | right | of | WARN in log | error |
|---|---|---|---|---|---|---|---|---|---|---|---|
| e4b | chat | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | chat | end | {} | default (no option) | temp 0 | [200] | [2051] | 1 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | generate | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | generate | end | {} | default (no option) | temp 0 | [200] | [2051] | 1 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | openai | start | {} | default (no option) | temp 0 | [200] | [2051] | 0 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | openai | end | {} | default (no option) | temp 0 | [200] | [2051] | 1 | 1 | {'limit': 2051, 'prompt': 9644, 'keep': 5, 'new': 2051} |  |
| e4b | chat | start | {"truncate": false} | default (no option) | temp 0 | [400] | [] | 0 | 1 |  | request (9644 tokens) exceeds the available context size (4096 tokens), try increasing it |
| e4b | generate | start | {"truncate": false} | default (no option) | temp 0 | [400] | [] | 0 | 1 |  | request (9644 tokens) exceeds the available context size (4096 tokens), try increasing it |
| e4b | chat | start | {"shift": false} | default (no option) | temp 0 | [400] | [] | 0 | 1 |  | the prompt is longer than the context length currently available to the model; shorten the prompt, adjust the context length in settings, or use a model with a longer context length |
