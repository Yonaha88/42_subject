/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   checker_bonus.c                                    :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/18 12:11:20 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/18 13:26:34 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "checker_bonus.h"

static t_list	*make_stack_checker(int argc, char *argv[])
{
	t_list	*a_lst;
	t_list	*tmp;
	int		i;
	int		err_flag;

	a_lst = NULL;
	i = 1;
	while (i < argc)
	{
		err_flag = 0;
		tmp = ft_lstnew(atoi_original(argv[i], &err_flag));
		if (!tmp || err_flag == -1 || detect_duplicate_values(a_lst,
				tmp->content) == -1)
		{
			free(tmp);
			ft_lstclear(&a_lst);
			write(2, "Error\n", 6);
			return (NULL);
		}
		ft_lstadd_back(&a_lst, tmp);
		i++;
	}
	return (a_lst);
}

static int	is_sorted_checker(t_list *a_lst, t_list *b_lst)
{
	t_list	*tmp;

	if (b_lst != NULL)
		return (0);
	tmp = a_lst;
	while (tmp && tmp->next)
	{
		if (tmp->content > tmp->next->content)
			return (0);
		tmp = tmp->next;
	}
	return (1);
}

static int	exec_op_checker(char *op, t_list **a_lst, t_list **b_lst)
{
	if (strcmp_original(op, "sa"))
		sa_checker(a_lst);
	else if (strcmp_original(op, "sb"))
		sb_checker(b_lst);
	else if (strcmp_original(op, "ss"))
		ss_checker(a_lst, b_lst);
	else if (strcmp_original(op, "pa"))
		pa_checker(a_lst, b_lst);
	else if (strcmp_original(op, "pb"))
		pb_checker(a_lst, b_lst);
	else if (strcmp_original(op, "ra"))
		ra_checker(a_lst);
	else if (strcmp_original(op, "rb"))
		rb_checker(b_lst);
	else if (strcmp_original(op, "rr"))
		rr_checker(a_lst, b_lst);
	else if (strcmp_original(op, "rra"))
		rra_checker(a_lst);
	else if (strcmp_original(op, "rrb"))
		rrb_checker(b_lst);
	else if (strcmp_original(op, "rrr"))
		rrr_checker(a_lst, b_lst);
	else
		return (-1);
	return (0);
}

static int	run_checker(t_list **a_lst, t_list **b_lst)
{
	char	*line;

	line = get_line_checker();
	while (line != NULL)
	{
		if (exec_op_checker(line, a_lst, b_lst) == -1)
		{
			free(line);
			ft_lstclear(a_lst);
			ft_lstclear(b_lst);
			write(2, "Error\n", 6);
			return (-1);
		}
		free(line);
		line = get_line_checker();
	}
	return (0);
}

int	main(int argc, char *argv[])
{
	t_list	*a_lst;
	t_list	*b_lst;

	a_lst = NULL;
	b_lst = NULL;
	if (argc < 2)
		return (0);
	if (error_handle(argc, argv) == 0)
		return (1);
	a_lst = make_stack_checker(argc, argv);
	if (!a_lst)
		return (1);
	if (run_checker(&a_lst, &b_lst) == -1)
		return (1);
	if (is_sorted_checker(a_lst, b_lst))
		write(1, "OK\n", 3);
	else
		write(1, "KO\n", 3);
	ft_lstclear(&a_lst);
	ft_lstclear(&b_lst);
	return (0);
}
