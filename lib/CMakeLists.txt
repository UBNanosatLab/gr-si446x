# Copyright 2011,2012,2016 Free Software Foundation, Inc.
#
# This file is part of GNU Radio
#
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})

list(APPEND si446x_sources
)

set(si446x_sources "${si446x_sources}" PARENT_SCOPE)
if(NOT si446x_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT si446x_sources)

add_library(gnuradio-si446x SHARED ${si446x_sources})
target_link_libraries(gnuradio-si446x ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-si446x PROPERTIES DEFINE_SYMBOL "gnuradio_si446x_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-si446x PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
include(GrMiscUtils)
GR_LIBRARY_FOO(gnuradio-si446x RUNTIME_COMPONENT "si446x_runtime" DEVEL_COMPONENT "si446x_devel")

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_si446x_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_si446x.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_si446x.cc
)

add_executable(test-si446x ${test_si446x_sources})

target_link_libraries(
  test-si446x
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-si446x
)

GR_ADD_TEST(test_si446x test-si446x)

########################################################################
# Print summary
########################################################################
message(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "Building for version: ${VERSION} / ${LIBVER}")

