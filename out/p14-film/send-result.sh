#!/bin/sh
# usage: send-result.sh N   (step 1 reply in /tmp/r1.json)
jq --argjson n "$1" --slurpfile r /tmp/r1.json '.messages += [
  {role:"assistant", content:($r[0].message.content // ""), tool_calls:$r[0].message.tool_calls},
  {role:"tool", tool_name:"multiply", content:"{\"result\": \($n)}"}]' /film/tool-12b.json |
curl -s $OLLAMA_HOST/api/chat -d @- | jq -r .message.content
