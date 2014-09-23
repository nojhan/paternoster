paternoster
===========

A command line tool that call the given command for each input line matching the given regular expression pattern.


## SYNOPSIS

`paternoster` [-h]

`paternoster` [-w] [-e] PATTERN COMMAND(S)


## DESCRIPTION

`paternoster` read lines of text stream on the standard input and call
*COMMAND(S)* for lines matching a given regular expression *PATTERN*.

If groups are specified in the regular expression pattern, only them are taken
into account, else the whole matching pattern is considered.

You can specify several commands when using groups by separating them with
spaces. If you indicate more commands than groups, the last ones will be
silently ignored.  If you ask for fewer commands, the last one will be
duplicated across remaining groups.


## OPTIONS

* `-h`, `--help`:
  Show a help message and exit

* `-w`, `--nowait`:
  Don't wait for the end of the current command before calling the next one.

* `-e`, `--end`:
  Run commands at the end of the input stream.

* `-g`, `--group`:
  Capture groups as arguments for the CMD, instead of running CMD for each group.
  CMD must have as many formating placeholder as captured groups.
  For example, if you capture 3 groups, you must put 3 formating placeholders in CMD:
    `paternoster --group "^(.*):(.*):(.*)$" "echo '>>> 1:%s 2:%s 3:%s <<<'"`


## EXAMPLES

* Make the speakers beep for every FIXME found in a source code:
 `cat paternoster.py | paternoster "FIXME" "beep"

* Play a sound for each error or warning on a compiler output (you must have the
  corresponding sound files in you path):
  `make 2>&1 | paternoster ".*(error|warning): .*$" "ogg123 %s.ogg"`

* Say out loud the error in a compiler output:
  `make 2>&1 | paternoster ".*(error: .*)$" "espeak --punct=';{}()' '%s'"`

* Play a series of sounds corresponding to the sequence of errors and warning
  at the end of a compilation:
  `make 2>&1 | paternoster --end ".*(error|warning): .*" "ogg123 %.ogg"`

* Notify the desktop every time a user logs in:
  `tail -n 2 -f /var/log/auth.log | paternoster ".*session opened for user ([^\s]+)\s*" "notify-send '%s login'"`

* Notify the desktop every time a user logs in or out:
  `tail -n 2 -f /var/log/auth.log | paternoster --group ".*session (opened|closed) for user ([^\s]+)\s*" "notify-send '%s %s'"`


## CREDITS

* Error sound by tcpp, licensed under CC-BY: http://www.freesound.org/people/tcpp/sounds/151309/

