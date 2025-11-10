set(MODULE mfile-root)

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

include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/mfile/include
)

root_generate_dictionary(G__${MODULE} ${HEADERS} MODULE ${MODULE} LINKDEF LinkDef.h)
add_library(${MODULE} SHARED ${SOURCES} G__${MODULE}.cxx)
add_library(hdtv::${MODULE} ALIAS ${MODULE})
target_link_libraries(${MODULE} PUBLIC ROOT::Core ROOT::Hist)

# Check endian-ness
include(TestBigEndian)
test_big_endian(BIGENDIAN)
if(NOT ${BIGENDIAN})
  target_compile_definitions(${MODULE} PRIVATE -DLOWENDIAN)
endif(NOT ${BIGENDIAN})

# Check for shared memory via sys/shm.h
include(CheckIncludeFile)
set(HAVE_SHM false)
check_include_file("sys/shm.h" HAVE_SHM)
if(NOT ${HAVE_SHM})
  target_compile_definitions(${MODULE} PRIVATE -DNO_SHM)
endif(NOT ${HAVE_SHM})

set_target_properties(${MODULE} PROPERTIES RESOURCE
    "${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}_rdict.pcm"
)

install(TARGETS ${MODULE} DESTINATION ${SKBUILD_PROJECT_NAME}/lib)
