cmake_minimum_required(VERSION 3.6 FATAL_ERROR)

# add_subdirectory(mfile)

project(mfile-root LANGUAGES C CXX)

set(SOURCES
    MatOp.cc
    MFileHist.cc
    MFileRoot.cc
    VMatrix.cc
    matop/matop_adjust.c
    matop/matop_conv.c
    matop/matop_project.c
    mfile/src/callindir.c
    mfile/src/converters.c
    mfile/src/disk_access.c
    mfile/src/getputint.c
    mfile/src/gf2_getput.c
    mfile/src/gf2_minfo.c
    mfile/src/lc_c1.c
    mfile/src/lc_c2.c
    mfile/src/lc_getput.c
    mfile/src/lc_minfo.c
    mfile/src/maccess.c
    mfile/src/mate_getput.c
    mfile/src/mate_minfo.c
    mfile/src/mat_types.c
    mfile/src/minfo.c
    mfile/src/mopen.c
    mfile/src/oldmat_getput.c
    mfile/src/oldmat_minfo.c
    mfile/src/shm_access.c
    mfile/src/shm_getput.c
    mfile/src/shm_minfo.c
    mfile/src/specio.c
    mfile/src/trixi_getput.c
    mfile/src/trixi_minfo.c
    mfile/src/txt_getput.c
    mfile/src/txt_minfo.c)

set(HEADERS
    MatOp.hh
    MFileHist.hh
    MFileRoot.hh
    VMatrix.hh
    matop/matop.h
    matop/matop_adjust.h
    matop/matop_conv.h
    matop/matop_project.h)

find_package(ROOT REQUIRED COMPONENTS Core Hist)
message(STATUS "ROOT Version ${ROOT_VERSION} found in ${ROOT_root_CMD}")
if(${ROOT_VERSION_MINOR} GREATER_EQUAL 20)
  include(${ROOT_DIR}/RootMacros.cmake)
elseif(${ROOT_VERSION_MINOR} EQUAL 19 AND EXISTS ${ROOT_DIR}/RootMacros.cmake)
  include(${ROOT_DIR}/RootMacros.cmake)
else()
  include(${ROOT_DIR}/modules/RootNewMacros.cmake)
endif()

root_generate_dictionary(
  G__${PROJECT_NAME}
  ${HEADERS}
  OPTIONS
  -I${CMAKE_CURRENT_SOURCE_DIR}/mfile/include/
  LINKDEF
  LinkDef.h)

add_library(${PROJECT_NAME} SHARED ${SOURCES} G__${PROJECT_NAME}.cxx)
add_library(hdtv::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
set_target_properties(
  ${PROJECT_NAME}
  PROPERTIES
    RESOURCE
    "${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${PROJECT_NAME}_rdict.pcm"
)
target_include_directories(
  ${PROJECT_NAME}
  PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}
         ${CMAKE_CURRENT_SOURCE_DIR}/matop
         ${CMAKE_CURRENT_SOURCE_DIR}/mfile/include
         ${CMAKE_CURRENT_SOURCE_DIR}/mfile/src)
target_link_libraries(${PROJECT_NAME} ROOT::Core ROOT::Hist)

# For mfile
target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
target_compile_options(${PROJECT_NAME} PRIVATE -ftrapv -Wall)
# Check endian-ness
include(TestBigEndian)
test_big_endian(BIGENDIAN)
if(NOT ${BIGENDIAN})
  target_compile_definitions(${PROJECT_NAME} PRIVATE -DLOWENDIAN)
endif(NOT ${BIGENDIAN})

install(
  TARGETS ${PROJECT_NAME}
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RESOURCE DESTINATION lib)
