INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_SI446X si446x)

FIND_PATH(
    SI446X_INCLUDE_DIRS
    NAMES si446x/api.h
    HINTS $ENV{SI446X_DIR}/include
        ${PC_SI446X_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    SI446X_LIBRARIES
    NAMES gnuradio-si446x
    HINTS $ENV{SI446X_DIR}/lib
        ${PC_SI446X_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/si446xTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(SI446X DEFAULT_MSG SI446X_LIBRARIES SI446X_INCLUDE_DIRS)
MARK_AS_ADVANCED(SI446X_LIBRARIES SI446X_INCLUDE_DIRS)
