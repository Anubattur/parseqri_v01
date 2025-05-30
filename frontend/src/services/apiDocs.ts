/**
 * API Documentation - Quick Reference
 * 
 * This file provides documentation for all API services available in the frontend.
 * Use this as a reference to understand available functionalities.
 */

import { authService, sqlService, visualizerService, datasetService, apiDiagnostic } from './api';

/**
 * Authentication Services
 * 
 * Handles user registration, login, authentication status and session management
 */
export const AuthAPI = {
  // Register a new user
  register: authService.register,
  
  // Log in an existing user
  login: authService.login,
  
  // Get the currently logged in user's details
  getCurrentUser: authService.getCurrentUser,
  
  // Check if the user is authenticated
  checkAuth: authService.checkAuth,
  
  // Log out the current user
  logout: authService.logout
};

/**
 * SQL Generation and Execution Services
 * 
 * Handles natural language to SQL conversion and query execution
 */
export const SQLAPI = {
  // Generate SQL from natural language query
  generateSql: sqlService.generateSql,
  
  // Validate an SQL query for syntax and other errors
  validateSql: sqlService.validateSql,
  
  // Execute an SQL query and get results
  executeSql: sqlService.executeSql,
  
  // All-in-one endpoint for text-to-SQL, execution and visualization
  processTextSQL: sqlService.processTextSQL
};

/**
 * Visualization Services
 * 
 * Handles creating visualizations from query results
 */
export const VisualizerAPI = {
  // Generate visualization for a specific query
  generateVisualization: visualizerService.generateVisualization,
  
  // Get recommended chart type based on data structure
  getRecommendedChartType: visualizerService.getRecommendedChartType,
  
  // Export data in various formats (CSV, JSON)
  exportData: visualizerService.exportData
};

/**
 * Dataset Management Services
 * 
 * Handles dataset listing, upload and inspection
 */
export const DatasetAPI = {
  // Get all datasets
  getDatasets: datasetService.getDatasets,
  
  // Upload a new dataset
  uploadDataset: datasetService.uploadDataset,
  
  // Get detailed information about a specific dataset
  getDatasetDetails: datasetService.getDatasetDetails
};

/**
 * Diagnostic Tools
 * 
 * Utilities for checking API status and connection
 */
export const DiagnosticAPI = {
  // Check if the API server is available
  checkAPIStatus: apiDiagnostic.checkAPIStatus,
  
  // Check token status and validity
  checkToken: apiDiagnostic.checkToken
};

/**
 * Usage Examples
 * 
 * How to use these API services:
 * 
 * // Authentication
 * const loginUser = async () => {
 *   try {
 *     const userData = await AuthAPI.login('username', 'password');
 *     console.log('Login successful', userData);
 *   } catch (error) {
 *     console.error('Login failed', error);
 *   }
 * };
 * 
 * // Generate SQL from text
 * const generateSqlQuery = async () => {
 *   try {
 *     const result = await SQLAPI.generateSql('Show me all customers from New York');
 *     console.log('Generated SQL:', result.sql);
 *   } catch (error) {
 *     console.error('SQL generation failed', error);
 *   }
 * };
 * 
 * // Create a visualization
 * const visualizeData = async (queryId: number) => {
 *   try {
 *     const chart = await VisualizerAPI.generateVisualization(queryId, 'bar');
 *     console.log('Chart data:', chart);
 *   } catch (error) {
 *     console.error('Visualization failed', error);
 *   }
 * };
 */ 