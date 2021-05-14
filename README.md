# cli

Organize your pebbles through CLI in your loved terminal

## Usage

```text
Usage: pebble.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create  Create a pebble
  delete  Delete a pebble
  get     Get a pebble
  list    List pebbles
  states  List states
  update  Update a pebble
```

### List pebbles

```bash
pebble list
```

Output:

```text
+---+-------------+---------------------+------------------------------------------+------------------------------------------+-------------+----------------+
| # |      ID     |      Created At     |                   NUID                   |                  Title                   |    State    |      Tags      |
+---+-------------+---------------------+------------------------------------------+------------------------------------------+-------------+----------------+
| 1 | WSbH9ghLQJv | 2021-05-13 10:56:37 |   dea0c9e9-76ee-4eb6-afda-ce32522fb350   |               Hello World                |      -      |     hello      |
| 2 | WGsWMnWp6Ci | 2021-05-13 10:34:30 |   ee6a2eab-5996-494a-851d-af3eee00b956   |            Sample Video #1382            | transcoding | vod,hls,ffmpeg |
| 3 | W7Bw7SNrGNn | 2021-05-12 16:01:31 | 381e56cf8ba9c70082476fe1379d5c7222f61475 | 381e56cf8ba9c70082476fe1379d5c7222f61475 |  uploaded   |   video,hls    |
| 4 | VwUAmYRCLZY | 2021-05-12 11:11:47 | 2a8195a4201f2f77d12467e116f7db9ee6b0ba42 | 2a8195a4201f2f77d12467e116f7db9ee6b0ba42 | transcoded  |   video,hls    |
+---+-------------+---------------------+------------------------------------------+------------------------------------------+-------------+----------------+
```

### Get a specified pebble

```bash
pebble get "WGsWMnWp6Ci" --json
```

Output:

```json
{
  "id": "WGsWMnWp6Ci",
  "created_at": "2021-05-13T10:34:30.555488+00:00",
  "updated_at": "2021-05-13T10:34:30.745542+00:00",
  "uuid": "bbdc1883-0d37-4ebd-bbdc-8050bfd3a75e",
  "namespace_id": "RbFmjJASDXG",
  "nuid": "ee6a2eab-5996-494a-851d-af3eee00b956",
  "owner_id": "Bi2r61CfxY1",
  "state_id": "Sm9PAC41nVg",
  "title": "Sample Video #1382",
  "filesize": 21,
  "content_type": "text/plain; charset=utf-8",
  "kind": "markdown",
  "tags": ["vod", "hls", "ffmpeg"],
  "revision": "19f15c52600164e8d34170dea20d7e5b",
  "permalink": "https://pebble.ggicci.me/p/WGsWMnWp6Ci/19f15c52600164e8d34170dea20d7e5b",
  "content": "Here's the content...",
  "storage_provider": "oss",
  "owner": null,
  "state": {
    "id": "Sm9PAC41nVg",
    "name": "transcoding",
    "display": "Transcoding"
  }
}
```
