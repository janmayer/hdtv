set(MODULE calibration)

set(HEADERS
    Calibration.hh
)

set(SOURCES
    Calibration.cc
)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

root_generate_dictionary(G__${MODULE} ${HEADERS} MODULE ${MODULE} LINKDEF LinkDef.h)
add_library(${MODULE} SHARED ${SOURCES} G__${MODULE}.cxx)
add_library(hdtv::${MODULE} ALIAS ${MODULE})
target_link_libraries(${MODULE} PUBLIC ROOT::Core ROOT::Hist ROOT::Graf ROOT::Gui)
set_target_properties(${MODULE} PROPERTIES RESOURCE
      "${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}_rdict.pcm"
    )

install(TARGETS ${MODULE} DESTINATION ${SKBUILD_PROJECT_NAME}/lib)
