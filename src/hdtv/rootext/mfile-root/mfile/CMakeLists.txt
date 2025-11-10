cmake_minimum_required(VERSION 3.6 FATAL_ERROR)
project(
  mfile
  VERSION 1.2
  LANGUAGES C)

set(SOURCES
    src/callindir.c
    src/converters.c
    src/disk_access.c
    src/getputint.c
    src/gf2_getput.c
    src/gf2_minfo.c
    src/lc_c1.c
    src/lc_c2.c
    src/lc_getput.c
    src/lc_minfo.c
    src/maccess.c
    src/mate_getput.c
    src/mate_minfo.c
    src/mat_types.c
    src/minfo.c
    src/mopen.c
    src/oldmat_getput.c
    src/oldmat_minfo.c
    src/shm_access.c
    src/shm_getput.c
    src/shm_minfo.c
    src/specio.c
    src/trixi_getput.c
    src/trixi_minfo.c
    src/txt_getput.c
    src/txt_minfo.c)

add_library(${PROJECT_NAME} SHARED ${SOURCES})
add_library(hdtv::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER include/mfile.h)

target_include_directories(
  ${PROJECT_NAME}
  PUBLIC $<INSTALL_INTERFACE:include> $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)

target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
target_compile_options(${PROJECT_NAME} PRIVATE -ftrapv -Wall)

# Check endian-ness
include(TestBigEndian)
test_big_endian(BIGENDIAN)
if(NOT ${BIGENDIAN})
  target_compile_definitions(${PROJECT_NAME} PRIVATE -DLOWENDIAN)
endif(NOT ${BIGENDIAN})

# Check for snprintf
include(CheckFunctionExists)
check_function_exists(snprintf HAVE_SNPRINTF)
if(${HAVE_SNPRINTF})
  target_compile_definitions(${PROJECT_NAME} PRIVATE -DHAVE_SNPRINTF)
endif(${HAVE_SNPRINTF})

# Check for shared memory via sys/shm.h
include(CheckIncludeFile)
set(HAVE_SHM false)
check_include_file("sys/shm.h" HAVE_SHM)
if(NOT ${HAVE_SHM})
  target_compile_definitions(${PROJECT_NAME} PRIVATE -DNO_SHM)
endif(NOT ${HAVE_SHM})

install(
  TARGETS ${PROJECT_NAME}
  EXPORT ${PROJECT_NAME}Config
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  PUBLIC_HEADER DESTINATION include)
install(
  EXPORT ${PROJECT_NAME}Config
  FILE ${PROJECT_NAME}Config.cmake
  NAMESPACE hdtv::
  DESTINATION share/${PROJECT_NAME}/cmake)
export(TARGETS ${PROJECT_NAME} FILE ${PROJECT_NAME}Config.cmake)

# Testing
enable_testing()
add_executable(check_mfile test/check_mfile.c)
target_link_libraries(check_mfile hdtv::mfile)
add_dependencies(check_mfile hdtv::mfile)
add_test(run_check_mfile check_mfile)
add_test(
  run_check_spectra
  md5sum
  -c
  ${CMAKE_CURRENT_SOURCE_DIR}/test/md5sums)
