set(MODULE fit)

set(SOURCES
    EEFitter.cc
    ExpBg.cc
    Fitter.cc
    Integral.cc
    InterpolationBg.cc
    Param.cc
    PolyBg.cc
    TheuerkaufFitter.cc
    Util.cc
)

set(HEADERS
    Background.hh
    EEFitter.hh
    ExpBg.hh
    Fitter.hh
    Integral.hh
    InterpolationBg.hh
    Option.hh
    Param.hh
    PolyBg.hh
    TheuerkaufFitter.hh
    Util.hh
)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

root_generate_dictionary(G__${MODULE} ${HEADERS} MODULE ${MODULE} LINKDEF LinkDef.h)
add_library(${MODULE} SHARED ${SOURCES} G__${MODULE}.cxx)
add_library(hdtv::${MODULE} ALIAS ${MODULE})
target_link_libraries(${MODULE} PUBLIC ROOT::Core ROOT::Hist ROOT::MathMore)

set_target_properties(${MODULE} PROPERTIES RESOURCE
  "${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}.rootmap;${CMAKE_CURRENT_BINARY_DIR}/lib${MODULE}_rdict.pcm"
)

install(TARGETS ${MODULE} DESTINATION ${SKBUILD_PROJECT_NAME}/lib)
