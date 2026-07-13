/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   bench_mark.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/17 10:35:05 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/19 18:25:10 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

int	judge_bench_flag(char ***argv, int *argc)
{
	int	bench_flag;

	bench_flag = 0;
	if (strcmp_original((*argv)[1], "--bench"))
	{
		bench_flag = 1;
		(*argv)++;
		(*argc)--;
	}
	return (bench_flag);
}

static void	write_strategy(t_data bench_data)
{
	if (bench_data.algo == 1)
		write(2, "Simple / O(n²)\n", 16);
	else if (bench_data.algo == 2)
		write(2, "Medium / O(n√n)\n", 18);
	else if (bench_data.algo == 3)
		write(2, "Complex / O(n log n)\n", 21);
	else
	{
		write(2, "Adaptive / ", 11);
		if (bench_data.dis < 2000)
			write(2, "O(n²)\n", 7);
		else if (bench_data.dis < 5000)
			write(2, "O(n√n)\n", 9);
		else
			write(2, "O(n log n)\n", 11);
	}
}

void	bench_mark(t_data bench_data)
{
	ft_printf("[bench] disorder:  ");
	ft_printf("%d.", bench_data.dis / 100);
	if (bench_data.dis % 100 < 10)
		write(2, "0", 1);
	ft_printf("%d%%\n", bench_data.dis % 100);
	ft_printf("[bench] strategy:  ");
	write_strategy(bench_data);
	ft_printf("[bench] total_ops: %d\n", bench_data.total);
	ft_printf("[bench] sa: %d  sb: %d  ss: %d  pa: %d  pb: %d\n",
		bench_data.sa_cnt, bench_data.sb_cnt, bench_data.ss_cnt,
		bench_data.pa_cnt, bench_data.pb_cnt);
	ft_printf("[bench] ra: %d  rb: %d  rr: %d  rra: %d  rrb: %d  rrr: %d\n",
		bench_data.ra_cnt, bench_data.rb_cnt, bench_data.rr_cnt,
		bench_data.rra_cnt, bench_data.rrb_cnt, bench_data.rrr_cnt);
}
