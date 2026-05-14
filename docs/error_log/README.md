# Error Log Filter Output

`error_log_filter.py` writes the filtered EU5 `error.log` here by default:

```text
docs/error_log/error.log
```

The generated `.log` file is intentionally ignored by git. Edit
`error_log_filter_config.json` to change the source path, output path, polling
interval, or vanilla-error filter file. Edit `vanilla_error_filters.txt` to
record known vanilla errors that should be removed from the filtered output.
You can paste a full `[HH:MM:SS]` log entry into that file; the next run will
rewrite it as an `exact:` rule with the timestamp removed.
