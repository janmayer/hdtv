/* Some system dependencies */

#ifndef SYSDEP_H_
#define SYSDEP_H_

/* Include autoconf 'config.h' */
// #if HAVE_CONFIG_H
// #include "config.h"
// #endif /* HAVE_CONFIG_H */

#if defined __CYGWIN32__ && !defined __CYGWIN__
/* For backwards compatibility with Cygwin b19 and
   earlier, we define __CYGWIN__ here, so that
   we can rely on checking just for that macro. */
#define __CYGWIN__ __CYGWIN32__
#endif

#if defined _WIN32 && !defined __CYGWIN__
/* Use Windows separators on all _WIN32 defining
   environments, except Cygwin. */
#define DIR_SEPARATOR_CHAR '\\'
#define DIR_SEPARATOR_STR "\\"
#define PATH_SEPARATOR_CHAR ';'
#define PATH_SEPARATOR_STR ";"
#endif
#ifndef DIR_SEPARATOR_CHAR
/* Assume that not having this is an indicator that all
   are missing. */
#define DIR_SEPARATOR_CHAR '/'
#define DIR_SEPARATOR_STR "/"
#define PATH_SEPARATOR_CHAR ':'
#define PATH_SEPARATOR_STR ":"
#endif /* !DIR_SEPARATOR_CHAR */

#endif /*SYSDEP_H_*/
