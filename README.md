paternoster
===========

A command line tool that call the given command for each input line matching the given regular expression pattern.


## SYNOPSIS

`paternoster` [-h]

`paternoster` [-w] PATTERN COMMAND(S)


## DESCRIPTION

`paternoster` read lines of text stream on the standard input and call
*COMMAND(S)* for lines matching a given regular expression *PATTERN*.

If groups are specified in the regular expression pattern, only them are taken
into account, else the whole matching pattern is considered.

You can specify several commands when using groups by separating them with
spaces. If you indicate more commands than groups, the last ones will be
silently ignored.  If you ask for fewer commands, the last one will be
duplicated across remaining groups.


## EXAMPLES

* Make the speakers beep for every FIXME found in a source code:
 `cat source.ext | paternoster "FIXME" "beep"

* Play a sound for each error or warning on a compiler output (you must have the
  corresponding wav files somewhere in you path):
  `make 2>&1 | paternoster ".*(error|warning): .*$" "play %s.wav"`

* Say out loud the error in a compiler output:
  `make 2>&1 | paternoster ".*(error: .*)$" "espeak --punct=';{}()' '%s'"`


## CREDITS

* Error sound by tcpp, licensed under CC-BY: http://www.freesound.org/people/tcpp/sounds/151309/
* 
