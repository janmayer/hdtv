#include "LC2Reader.h"
#include "mfile-tiny.h"
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>

using namespace std;

/* See root.cern.ch/root/Using.html for some info on adding classes to ROOT */

LC2Reader::LC2Reader()
{
	header = NULL;
	poslen_tbl = NULL;
	handle = 0;
}

LC2Reader::~LC2Reader()
{
	Close();
}

int LC2Reader::Open(char *filename)
{
	if(handle > 0)  // Some file is already open
		return kRuntimeError;
		
	handle = open(filename, O_RDONLY);
	
	if(handle < 0)   // Error opening file
		return kIOError;
		
	return kSuccess;
}

int LC2Reader::Close(void)
{
	int retval;
	
	if(header) {
		free_lc_header(header);
		header = NULL;
	}
		
	if(poslen_tbl) {
		free_poslen_tbl(poslen_tbl);
		poslen_tbl = NULL;
	}
	
	if(handle <= 0)    // it is OK to call Close() several times
		return kSuccess;
		
	retval = close(handle);
	
	if(retval < 0)
		return kIOError;
		
	handle = 0;
	return kSuccess;
}

int LC2Reader::Probe(void)
{
	if(handle <= 0)
		return kRuntimeError;
	
	if(!header) {
		header = alloc_lc_header();
		if(!header)
			return kMemError;
			
		/* Reading the header is allowed to fail here,
			but we will then consider the spectrum invalid. */
		if(read_lc_header(handle, header) < 0)
			return 0;
	}
		
	if(check_lc2(header))
		return 1;
	else
		return 0;
}

int LC2Reader::EnsureHeader(void)
{
    if(handle <= 0)
		return kRuntimeError;

	if(!header) {
		header = alloc_lc_header();
		if(!header)
			return kMemError;
			
		if(read_lc_header(handle, header) < 0)
			return kIOError;
	}
	
	return kSuccess;
}

int LC2Reader::GetNumBins(void)
{
	int hstat = EnsureHeader();
	if(hstat != kSuccess)
	    return hstat;
	
	return header->columns;
}

int LC2Reader::GetNumLines(void)
{
	int hstat = EnsureHeader();
	if(hstat != kSuccess)
	    return hstat;
	
	return header->lines;
}

int LC2Reader::Fill(TH1 *hist, int idx)
{
	char *cspec;
	int *spec;
	int i;
	int hstat = EnsureHeader();
	
	if(hstat != kSuccess)
	    return hstat;
	
	if(!poslen_tbl) {
		poslen_tbl = alloc_poslen_tbl(header);
		if(!poslen_tbl)
			return kMemError;
			
		if(read_poslen_tbl(handle, header, poslen_tbl) < 0)
			return kIOError;
	}
	
	cspec = alloc_cspec(idx, poslen_tbl);
	if(!cspec)
		return kMemError;
		
	if(read_cspec(handle, idx, poslen_tbl, cspec) < 0) {
		free_cspec(cspec);
		return kIOError;
	}
	
	spec = alloc_spec(header->columns);
	if(!spec) {
		free_cspec(cspec);
		return kMemError;
	}
	
	if(lc2_uncompress(spec, cspec, header->columns) != header->columns) {
		free_cspec(cspec);
		free_spec(spec);
		return kRuntimeError;
	}
	
	for(i=0; i<header->columns; i++) {
		hist->SetBinContent(i+1, (double)spec[i]);
	}
	
	free_cspec(cspec);
	free_spec(spec);
	
	return kSuccess;
}

int LC2Reader::FillMatrix(TH2 *hist)
{
	char *cspec;
	int *spec;
	int i, idx;
	int result;
	
	result = EnsureHeader();
	if(result != kSuccess)
	    return result;
	
	if(!poslen_tbl) {
		poslen_tbl = alloc_poslen_tbl(header);
		if(!poslen_tbl)
			return kMemError;
			
		if(read_poslen_tbl(handle, header, poslen_tbl) < 0)
			return kIOError;
	}
	
	spec = alloc_spec(header->columns);
	if(!spec) {
		free_cspec(cspec);
		return kMemError;
	}
	
	result = kSuccess;
	
	for(idx=0; idx < header->lines;	idx++) {
		cspec = alloc_cspec(idx, poslen_tbl);
		if(!cspec) {
			result = kMemError;
			break;
		}
	
		if(read_cspec(handle, idx, poslen_tbl, cspec) < 0) {
			result = kIOError;
			free_cspec(cspec);
			break;
		}
	
		if(lc2_uncompress(spec, cspec, header->columns) != header->columns) {
			result = kRuntimeError;
			free_cspec(cspec);
			break;
		}
	
		for(i=0; i<header->columns; i++) {
			hist->SetBinContent(i+1, idx, (double)spec[i]);
		}
		
		free_cspec(cspec);
	}
	
	free_spec(spec);
	
	return result;
}

