cmake_minimum_required(VERSION 3.15)

project(
  mfile
  VERSION 1.2
  LANGUAGES C)

include(TestBigEndian)
include(CheckFunctionExists)
include(CheckIncludeFile)

add_library(
  ${PROJECT_NAME} SHARED
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

set_target_properties(${PROJECT_NAME} PROPERTIES PUBLIC_HEADER include/mfile.h)

target_include_directories(
  ${PROJECT_NAME}
  PUBLIC include
  PRIVATE src)

target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
target_compile_options(${PROJECT_NAME} PRIVATE -ftrapv -Wall)

test_big_endian(IS_BIGENDIAN)
if(NOT IS_BIGENDIAN)
  target_compile_definitions(${PROJECT_NAME} PRIVATE LOWENDIAN)
endif()

check_function_exists(snprintf HAVE_SNPRINTF)
if(HAVE_SNPRINTF)
  target_compile_definitions(${PROJECT_NAME} PRIVATE HAVE_SNPRINTF)
endif()

check_include_file("sys/shm.h" HAVE_SHM)
if(NOT HAVE_SHM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE NO_SHM)
endif()

install(
  TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION lib
  PUBLIC_HEADER DESTINATION include)

enable_testing()

add_executable(check_${PROJECT_NAME} test/check_mfile.c)
target_link_libraries(check_${PROJECT_NAME} PRIVATE ${PROJECT_NAME})

add_test(NAME run_check_${PROJECT_NAME} COMMAND check_${PROJECT_NAME})
add_test(NAME run_check_spectra COMMAND md5sum -c ${CMAKE_CURRENT_SOURCE_DIR}/test/md5sums)
