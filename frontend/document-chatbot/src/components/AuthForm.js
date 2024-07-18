import React from 'react';
import styled from 'styled-components';

const PageContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
  font-family: 'Roboto', sans-serif;
`;

const FormContainer = styled.div`
  max-width: 400px;
  width: 100%;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background-color: #fff;
  transition: transform 0.3s, box-shadow 0.3s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  }
`;

const Title = styled.h2`
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-weight: 700;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
`;

const Input = styled.input`
  margin: 15px 0;
  padding: 15px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 30px;
  transition: border-color 0.3s;

  &:focus {
    border-color: #6200ea;
    outline: none;
    box-shadow: 0 0 5px rgba(98, 0, 234, 0.1);
  }
`;

const Button = styled.button`
  margin: 20px 0;
  padding: 15px;
  font-size: 16px;
  font-weight: 600;
  background-color: #6200ea;
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.3s;

  &:hover {
    background-color: #3700b3;
    transform: translateY(-3px);
  }

  &:active {
    transform: translateY(0);
  }
`;

export const AuthForm = ({ title, onSubmit, submitText }) => {
  return (
    <PageContainer>
      <FormContainer>
        <Title>{title}</Title>
        <Form onSubmit={onSubmit}>
          <Input type="text" name="username" placeholder="Username" required />
          <Input type="password" name="password" placeholder="Password" required />
          <Button type="submit">{submitText}</Button>
        </Form>
      </FormContainer>
    </PageContainer>
  );
};